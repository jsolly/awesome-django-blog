#!/usr/bin/env bash
# Install skills, agents, and cited rules from a private dotagents checkout into
# Cursor Cloud Agent home paths.
# Skills → ~/.cursor/skills; agents → ~/.cursor/agents;
# cited rules → ~/.cursor/dotagents-package/rules
# Idempotent: safe to re-run from environment.json install/update.
#
# Source (first match):
#   1. $DOTAGENTS_ROOT if it looks like this repo
#   2. The checkout that contains this script, if it looks like this repo
#      (templates/cloud-agent/ or a .cursor/ copy inside dotagents itself)
#   3. $HOME/code/dotagents if present
#   4. Shallow clone of this private repo ($DOTAGENTS_CLONE_URL, default
#      https://github.com/jsolly/dotagents.git)
# Never clones a public skills mirror. Does not vendor the full private tree
# into the child repo working tree — copies only into VM home paths.
# Laptop-only skills stay off cloud VMs (skills/laptop-only.txt).
# skills/work-excluded.txt is a same-name alias for already-copied child installers.
set -euo pipefail

SKILLS_HOME="${CURSOR_CLOUD_SKILLS_HOME:-${HOME}/.cursor/skills}"
AGENTS_HOME="${CURSOR_CLOUD_AGENTS_HOME:-${HOME}/.cursor/agents}"
RULES_HOME="${CURSOR_CLOUD_PACKAGE_RULES:-${HOME}/.cursor/dotagents-package/rules}"

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

root=""
if root="$(resolve_root)"; then
  echo "cloud-package: using local checkout $root"
else
  clone_url="${DOTAGENTS_CLONE_URL:-https://github.com/jsolly/dotagents.git}"
  clone_ref="${DOTAGENTS_CLONE_REF:-main}"
  clone_tmp="$(mktemp -d)"
  echo "cloud-package: no local checkout; cloning ${clone_url}@${clone_ref} (shallow, sparse)"
  if ! git clone --depth 1 --filter=blob:none --sparse --branch "$clone_ref" \
    "$clone_url" "$clone_tmp/dotagents"; then
    echo "cloud-package: ERROR — set DOTAGENTS_ROOT to a host-local checkout of the private dotagents repo (laptop: ~/code/dotagents)." >&2
    exit 1
  fi
  git -C "$clone_tmp/dotagents" sparse-checkout set skills agents rules
  root="$clone_tmp/dotagents"
  if ! looks_like_dotagents "$root"; then
    echo "cloud-package: ERROR — clone at $root is not a dotagents checkout" >&2
    exit 1
  fi
fi

read_laptop_only "$root"

# --- skills (required) ---
src_skills="$root/skills"
if [[ ! -d "$src_skills" ]]; then
  echo "cloud-package: ERROR — no skills/ directory in checkout $root" >&2
  exit 1
fi

mkdir -p "$SKILLS_HOME"
installed_skills=0
skipped_excluded=0
for skill_dir in "$src_skills"/*/; do
  [[ -d "$skill_dir" ]] || continue
  name="$(basename "$skill_dir")"
  if is_laptop_only "$name"; then
    echo "cloud-package: skip skill ${name} (laptop-only)"
    skipped_excluded=$((skipped_excluded + 1))
    continue
  fi
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "cloud-package: skip skill ${name} (no SKILL.md)"
    continue
  fi
  dest="$SKILLS_HOME/$name"
  rm -rf "$dest"
  cp -R "$skill_dir" "$dest"
  installed_skills=$((installed_skills + 1))
  echo "cloud-package: installed skill ${name} → ${dest}"
done

if [[ "$installed_skills" -eq 0 ]]; then
  echo "cloud-package: ERROR — no skills installed from $root" >&2
  exit 1
fi

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

echo "cloud-package: done (${installed_skills} skill(s), ${skipped_excluded} laptop-only skipped, ${installed_agents} agent file(s), ${installed_rules} rule file(s))"
