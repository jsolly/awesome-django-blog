#!/usr/bin/env bash
# Install skills, agents, cited rules, the connector/plugin catalog, and the shared
# pre-commit gate lib from a private dotagents checkout into Cursor Cloud Agent home paths.
# Skills → ~/.cursor/skills; agents → ~/.cursor/agents;
# cited rules → ~/.cursor/dotagents-package/rules;
# mcps/catalog.json → ~/.cursor/dotagents-package/mcps (so /optimize-workspaces can reconcile live
# connectors/plugins against the canon on a VM with no laptop checkout);
# gate/gate-lib.sh → ~/.cursor/dotagents-package/gate/gate-lib.sh (DOTAGENTS_GATE_LIB) plus a
# stub symlink at ~/code/dotagents/gate/gate-lib.sh so child-repo pre-commit shims that
# default to that path still work. The stub is not a full checkout.
# Idempotent: safe to re-run from environment.json install/update.
#
# Source (first match):
#   1. $DOTAGENTS_ROOT if it looks like this repo
#   2. The checkout that contains this script, if it looks like this repo
#      (templates/cloud-agent/ or a .cursor/ copy inside dotagents itself)
#   3. $HOME/code/dotagents if it looks like this repo (skills+agents+rules; a
#      gate-lib stub alone does not count)
#   4. Fetch this private repo ($DOTAGENTS_CLONE_URL, default
#      https://github.com/jsolly/dotagents.git), preferring credentials gh already
#      has, then falling back to git clone:
#        a. gh api tarball
#        b. gh repo clone (shallow, sparse)
#        c. git clone --depth 1 --sparse (same as the historical fallback)
# Never clones a public skills mirror. Does not vendor the full private tree
# into the child repo working tree — copies only into VM home paths.
# Laptop-only skills stay off cloud VMs (skills/laptop-only.txt).
# skills/work-excluded.txt is a same-name alias for already-copied child installers.
# Re-runs prune dest skill dirs that are retired or now laptop-only so a leftover
# copied playbook (for example a deleted skills/integration-verify) cannot stay loadable.
set -euo pipefail

SKILLS_HOME="${CURSOR_CLOUD_SKILLS_HOME:-${HOME}/.cursor/skills}"
AGENTS_HOME="${CURSOR_CLOUD_AGENTS_HOME:-${HOME}/.cursor/agents}"
RULES_HOME="${CURSOR_CLOUD_PACKAGE_RULES:-${HOME}/.cursor/dotagents-package/rules}"
MCPS_HOME="${CURSOR_CLOUD_PACKAGE_MCPS:-${HOME}/.cursor/dotagents-package/mcps}"
GATE_HOME="${CURSOR_CLOUD_PACKAGE_GATE:-${HOME}/.cursor/dotagents-package/gate}"
GATE_LIB_PATH="${GATE_HOME}/gate-lib.sh"
# Sparse fetch set. skills+agents+rules are required for looks_like_dotagents;
# mcps carries the connector catalog; gate carries gate-lib.sh for child pre-commits.
CLOUD_SPARSE_DIRS=(skills agents rules mcps gate)

looks_like_dotagents() {
  local root="$1"
  [[ -n "$root" && -d "$root/skills" && -d "$root/agents" && -d "$root/rules" ]] || return 1
  local f
  shopt -s nullglob
  for f in "$root/skills"/*/SKILL.md; do
    shopt -u nullglob
    [[ -f "$f" ]] && return 0
  done
  shopt -u nullglob
  return 1
}

append_skip_names() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  local line
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" ]] && continue
    LAPTOP_ONLY+=("$line")
  done < "$file"
}

read_laptop_only() {
  local root="$1"
  LAPTOP_ONLY=()
  append_skip_names "$root/skills/laptop-only.txt"
  # Alias: already-copied child-repo installers still read work-excluded.txt
  # from a clone of this repo. Union so either filename skips the same skills.
  append_skip_names "$root/skills/work-excluded.txt"
}

is_laptop_only() {
  local name="$1" x
  for x in "${LAPTOP_ONLY[@]+"${LAPTOP_ONLY[@]}"}"; do
    [[ "$x" == "$name" ]] && return 0
  done
  return 1
}

clone_tmp=""
cleanup() {
  if [[ -n "$clone_tmp" ]]; then
    rm -rf "$clone_tmp"
  fi
}
trap cleanup EXIT

resolve_root() {
  local script_dir repo
  if looks_like_dotagents "${DOTAGENTS_ROOT:-}"; then
    printf '%s\n' "$(cd "$DOTAGENTS_ROOT" && pwd)"
    return 0
  fi
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  # templates/cloud-agent/install-cloud-skills.sh → repo root
  repo="$(cd "$script_dir/../.." && pwd)"
  if looks_like_dotagents "$repo"; then
    printf '%s\n' "$repo"
    return 0
  fi
  # .cursor/install-cloud-skills.sh inside a dotagents checkout
  repo="$(cd "$script_dir/.." && pwd)"
  if looks_like_dotagents "$repo"; then
    printf '%s\n' "$repo"
    return 0
  fi
  if looks_like_dotagents "${HOME}/code/dotagents"; then
    printf '%s\n' "$(cd "${HOME}/code/dotagents" && pwd)"
    return 0
  fi
  return 1
}

# Drop userinfo so https://token@github.com/org/repo still maps to org/repo
# and never appears in installer logs.
strip_url_userinfo() {
  local url="$1" scheme after
  if [[ "$url" == *://*@* ]]; then
    scheme="${url%%://*}"
    after="${url#*://}"
    after="${after#*@}"
    printf '%s://%s\n' "$scheme" "$after"
    return 0
  fi
  printf '%s\n' "$url"
}

# Map a git remote URL to GitHub owner/repo. Non-github URLs (file:// fixtures) fail.
github_nwo_from_url() {
  local url="$1" rest owner repo
  url="$(strip_url_userinfo "$url")"
  url="${url%%#*}"
  url="${url%%\?*}"
  url="${url%/}"
  url="${url%.git}"
  case "$url" in
    https://github.com/* | http://github.com/*)
      rest="${url#*github.com/}"
      ;;
    git@github.com:*)
      rest="${url#git@github.com:}"
      ;;
    ssh://git@github.com/*)
      rest="${url#ssh://git@github.com/}"
      ;;
    github.com/*)
      rest="${url#github.com/}"
      ;;
    *)
      return 1
      ;;
  esac
  rest="${rest#/}"
  owner="${rest%%/*}"
  rest="${rest#"$owner"}"
  rest="${rest#/}"
  repo="${rest%%/*}"
  [[ -n "$owner" && -n "$repo" && "$owner" != *"/"* ]] || return 1
  printf '%s/%s\n' "$owner" "$repo"
}

sparse_checkout() {
  local dest="$1"
  git -C "$dest" sparse-checkout set "${CLOUD_SPARSE_DIRS[@]}"
}

# GitHub tarballs unpack to a single {owner}-{repo}-{sha}/ prefix. Extract only
# the sparse dirs so ONE-FILE-DOCUMENT.md and other laptop files stay out.
unpack_github_tarball() {
  local tarball="$1" dest="$2"
  local prefix d
  prefix=""
  while IFS= read -r d; do
    prefix="${d%%/*}"
    break
  done < <(tar -tzf "$tarball")
  [[ -n "$prefix" ]] || return 1
  mkdir -p "$dest"
  for d in "${CLOUD_SPARSE_DIRS[@]}"; do
    tar -xzf "$tarball" -C "$dest" --strip-components=1 "${prefix}/${d}" 2>/dev/null || true
  done
  looks_like_dotagents "$dest"
}

fetch_via_gh_tarball() {
  local nwo="$1" ref="$2" dest="$3"
  local tarball
  command -v gh >/dev/null 2>&1 || return 1
  echo "cloud-package: fetching ${nwo}@${ref} via gh api tarball"
  rm -rf "$dest"
  mkdir -p "$dest"
  tarball="$(mktemp "${clone_tmp}/tarball.XXXXXX")"
  if ! GH_PAGER=cat gh api "repos/${nwo}/tarball/${ref}" >"$tarball"; then
    echo "cloud-package: gh api tarball failed for ${nwo}@${ref}"
    return 1
  fi
  if [[ ! -s "$tarball" ]]; then
    echo "cloud-package: gh api tarball returned an empty body"
    return 1
  fi
  unpack_github_tarball "$tarball" "$dest"
}

fetch_via_gh_repo_clone() {
  local nwo="$1" ref="$2" dest="$3"
  command -v gh >/dev/null 2>&1 || return 1
  echo "cloud-package: cloning ${nwo}@${ref} via gh repo clone (shallow, sparse)"
  rm -rf "$dest"
  GH_PAGER=cat gh repo clone "$nwo" "$dest" -- --depth 1 --filter=blob:none --sparse --branch "$ref" || return 1
  sparse_checkout "$dest"
  looks_like_dotagents "$dest"
}

fetch_via_git_clone() {
  local url="$1" ref="$2" dest="$3"
  echo "cloud-package: cloning $(strip_url_userinfo "$url")@${ref} via git clone (shallow, sparse)"
  rm -rf "$dest"
  GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=true git clone --depth 1 --filter=blob:none --sparse --branch "$ref" \
    "$url" "$dest" || return 1
  sparse_checkout "$dest"
  looks_like_dotagents "$dest"
}

fetch_failed() {
  local url="$1" ref="$2"
  echo "cloud-package: ERROR — could not fetch private dotagents ($(strip_url_userinfo "$url")@${ref})." >&2
  echo "cloud-package: Set DOTAGENTS_ROOT to a checkout of jsolly/dotagents, or grant this environment git/gh access to that repo (GitHub App allowlist + environment.json repositoryDependencies: github.com/jsolly/dotagents). GitHub MCP read access is not git clone credentials. Do not vendor the private tree into this working copy." >&2
  exit 1
}

append_gate_exports() {
  local rc="$1"
  touch "$rc"
  if ! grep -q 'DOTAGENTS_GATE_LIB=' "$rc" 2>/dev/null; then
    cat >>"$rc" <<EOF

# Cloud Agent shared pre-commit gate lib (not a ~/code/dotagents checkout)
export DOTAGENTS_GATE_LIB="${GATE_LIB_PATH}"
EOF
  fi
}

install_gate_lib() {
  local src="$1/gate/gate-lib.sh"
  local stub="${HOME}/code/dotagents/gate/gate-lib.sh"
  mkdir -p "$GATE_HOME"
  cp -f "$src" "$GATE_LIB_PATH"
  export DOTAGENTS_GATE_LIB="$GATE_LIB_PATH"
  append_gate_exports "${HOME}/.bashrc"
  append_gate_exports "${HOME}/.profile"
  # Child shims default to $HOME/code/dotagents/gate/gate-lib.sh. A stub symlink
  # keeps git hooks working when DOTAGENTS_GATE_LIB is unset (non-login bash -c).
  # Do not replace a real checkout's gate-lib.sh (looks_like_dotagents).
  if ! looks_like_dotagents "${HOME}/code/dotagents"; then
    mkdir -p "$(dirname "$stub")"
    ln -sfn "$GATE_LIB_PATH" "$stub"
  fi
  echo "cloud-package: installed gate lib → ${GATE_LIB_PATH}"
  return 0
}

root=""
if root="$(resolve_root)"; then
  echo "cloud-package: using local checkout $root"
else
  clone_url="${DOTAGENTS_CLONE_URL:-https://github.com/jsolly/dotagents.git}"
  clone_ref="${DOTAGENTS_CLONE_REF:-main}"
  clone_tmp="$(mktemp -d)"
  dest="$clone_tmp/dotagents"
  nwo=""
  fetched=0
  echo "cloud-package: no local checkout; fetching $(strip_url_userinfo "$clone_url")@${clone_ref} (authenticated gh, then git clone; sparse)"
  if nwo="$(github_nwo_from_url "$clone_url")"; then
    if fetch_via_gh_tarball "$nwo" "$clone_ref" "$dest"; then
      fetched=1
    elif fetch_via_gh_repo_clone "$nwo" "$clone_ref" "$dest"; then
      fetched=1
    fi
  fi
  if [[ "$fetched" -eq 0 ]]; then
    if fetch_via_git_clone "$clone_url" "$clone_ref" "$dest"; then
      fetched=1
    fi
  fi
  if [[ "$fetched" -eq 0 ]]; then
    fetch_failed "$clone_url" "$clone_ref"
  fi
  root="$dest"
  if ! looks_like_dotagents "$root"; then
    echo "cloud-package: ERROR — fetch at $root is not a dotagents checkout" >&2
    fetch_failed "$clone_url" "$clone_ref"
  fi
fi

read_laptop_only "$root"

src_skills="$root/skills"
if [[ ! -d "$src_skills" ]]; then
  echo "cloud-package: ERROR — no skills/ directory in checkout $root" >&2
  exit 1
fi

# Currently shipped = source SKILL.md and not laptop-only. Copy and prune
# both use this so a new skip reason cannot leave a leftover dest loadable.
should_ship_skill() {
  local name="$1"
  [[ -f "$src_skills/$name/SKILL.md" ]] || return 1
  if is_laptop_only "$name"; then
    return 1
  fi
  return 0
}

# --- skills (required) ---

mkdir -p "$SKILLS_HOME"
installed_skills=0
skipped_excluded=0
for skill_dir in "$src_skills"/*/; do
  [[ -d "$skill_dir" ]] || continue
  name="$(basename "$skill_dir")"
  if ! should_ship_skill "$name"; then
    if is_laptop_only "$name"; then
      echo "cloud-package: skip skill ${name} (laptop-only)"
      skipped_excluded=$((skipped_excluded + 1))
    else
      echo "cloud-package: skip skill ${name} (no SKILL.md)"
    fi
    continue
  fi
  dest="$SKILLS_HOME/$name"
  if [[ -L "$dest" ]]; then
    rm -f -- "$dest"
  else
    rm -rf -- "$dest"
  fi
  cp -R "$skill_dir" "$dest"
  installed_skills=$((installed_skills + 1))
  echo "cloud-package: installed skill ${name} → ${dest}"
done

if [[ "$installed_skills" -eq 0 ]]; then
  echo "cloud-package: ERROR — no skills installed from $root" >&2
  exit 1
fi

# Copy skips laptop-only names without deleting a previous dest copy, and never
# sees retired names that left the source tree. Drop dest skill dirs that are
# no longer shipped (missing source SKILL.md, or now laptop-only). Leave dest
# dirs that are not skills (no SKILL.md) alone. Directory symlinks are unlinked
# only — never `rm -rf symlink/`, which follows the referent.
# SKILLS_HOME is this installer's reconstitution dest on Cloud Agent VMs.
pruned_skills=0
shopt -s nullglob
for dest_path in "$SKILLS_HOME"/*; do
  dest_dir="${dest_path%/}"
  [[ -e "$dest_dir" || -L "$dest_dir" ]] || continue
  name="$(basename "$dest_dir")"
  if [[ -L "$dest_dir" ]]; then
    if should_ship_skill "$name"; then
      continue
    fi
    rm -f -- "$dest_dir"
    pruned_skills=$((pruned_skills + 1))
    echo "cloud-package: pruned retired skill ${name}"
    continue
  fi
  if [[ ! -d "$dest_dir" || ! -f "$dest_dir/SKILL.md" ]]; then
    continue
  fi
  if should_ship_skill "$name"; then
    continue
  fi
  rm -rf -- "$dest_dir"
  pruned_skills=$((pruned_skills + 1))
  echo "cloud-package: pruned retired skill ${name}"
done
shopt -u nullglob

# --- agents ---
src_agents="$root/agents"
installed_agents=0
if [[ ! -d "$src_agents" ]]; then
  echo "cloud-package: ERROR — no agents/ in checkout $root" >&2
  exit 1
fi
mkdir -p "$AGENTS_HOME"
shopt -s nullglob
for agent_file in "$src_agents"/*.md; do
  name="$(basename "$agent_file")"
  dest="$AGENTS_HOME/$name"
  cp -f "$agent_file" "$dest"
  installed_agents=$((installed_agents + 1))
  echo "cloud-package: installed agent ${name} → ${dest}"
done
shopt -u nullglob
if [[ "$installed_agents" -eq 0 ]]; then
  echo "cloud-package: ERROR — agents/ present but empty at $src_agents" >&2
  exit 1
fi

# --- cited rules ---
src_rules="$root/rules"
installed_rules=0
if [[ ! -d "$src_rules" ]]; then
  echo "cloud-package: ERROR — no rules/ in checkout $root" >&2
  exit 1
fi
mkdir -p "$RULES_HOME"
shopt -s nullglob
for rule_file in "$src_rules"/*.md; do
  name="$(basename "$rule_file")"
  dest="$RULES_HOME/$name"
  cp -f "$rule_file" "$dest"
  installed_rules=$((installed_rules + 1))
  echo "cloud-package: installed rule ${name} → ${dest}"
done
shopt -u nullglob
if [[ "$installed_rules" -eq 0 ]]; then
  echo "cloud-package: ERROR — rules/ present but empty at $src_rules" >&2
  exit 1
fi

# --- connector/plugin catalog ---
# The cloud-first canon for MCP servers and marketplace plugins. Copied (not required) so an older
# checkout still installs skills — a missing catalog degrades /optimize-workspaces's reconciliation to
# "canon unavailable", which the receipt discloses rather than inventing green.
installed_catalog=0
src_catalog="$root/mcps/catalog.json"
if [[ -f "$src_catalog" ]]; then
  mkdir -p "$MCPS_HOME"
  cp -f "$src_catalog" "$MCPS_HOME/catalog.json"
  installed_catalog=1
  echo "cloud-package: installed connector catalog → ${MCPS_HOME}/catalog.json"
  if [[ -f "$root/mcps/README.md" ]]; then
    cp -f "$root/mcps/README.md" "$MCPS_HOME/README.md"
  fi
else
  # These two files are installer-owned. An older checkout must not leave a
  # previous revision looking like current canon to /optimize-workspaces.
  rm -f "$MCPS_HOME/catalog.json" "$MCPS_HOME/README.md"
  echo "cloud-package: WARN — no mcps/catalog.json in $root; /optimize-workspaces cannot reconcile connectors against the canon" >&2
fi

# --- shared pre-commit gate lib ---
# Self-contained (gate/ has no siblings). Missing lib warns; skill install still succeeds so an
# older checkout can boot. Child repos must not vendor a local copy of gate-lib.sh.
installed_gate=0
if [[ -f "$root/gate/gate-lib.sh" ]]; then
  install_gate_lib "$root"
  installed_gate=1
else
  echo "cloud-package: WARN — no gate/gate-lib.sh in $root; child-repo pre-commits that source DOTAGENTS_GATE_LIB will fail. Do not hand-copy gate-lib.sh into the child working tree." >&2
fi

echo "cloud-package: done (${installed_skills} skill(s), ${skipped_excluded} laptop-only skipped, ${pruned_skills} retired skill(s) pruned, ${installed_agents} agent file(s), ${installed_rules} rule file(s), ${installed_catalog} catalog file(s), ${installed_gate} gate lib(s))"
