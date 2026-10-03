#!/usr/bin/env bash
# Cursor Cloud Agent bootstrap: find or fetch a private dotagents checkout, then run that checkout's
# templates/cloud-agent/install-cloud-package.sh, which does the install (see its header).
# Every fleet child carries this file byte-equal as .cursor/install-cloud-skills.sh
# (/optimize-workspaces cloud-package sync), so it knows only where the package installer lives:
# what gets installed, and how, travels with the checkout and needs no fleet re-sync; a change to
# this file does. Running the checkout's script adds no trust: the VM already follows dotagents'
# skills and sources its gate/gate-lib.sh from every child pre-commit.
# Idempotent: safe to re-run from environment.json install/update.
#
# Source (first match that holds the package installer):
#   1. $DOTAGENTS_ROOT
#   2. The dotagents checkout this script sits in, when it runs from templates/cloud-agent/ (never a
#      child's .cursor/ copy, whose parent directories are not dotagents)
#   3. $HOME/code/dotagents (a gate-lib stub there does not count)
#   4. Fetch jsolly/dotagents at $DOTAGENTS_CLONE_REF (default main), preferring credentials gh
#      already has, then falling back to git clone (whose credential helper supplies any token):
#        a. gh api tarball
#        b. gh repo clone (shallow)
#        c. git clone --depth 1 https://github.com/jsolly/dotagents.git
#      into a temp dir removed on exit, never into the child repo working tree. A fetched ref without
#      the package installer (older than this bootstrap) fails closed.
# The repo is fixed: a VM that needs another transport clones it first and sets DOTAGENTS_ROOT. No
# URL here ever carries a credential, so nothing needs redacting. Never clones a public skills mirror.
set -euo pipefail

PACKAGE_INSTALLER="templates/cloud-agent/install-cloud-package.sh"
DOTAGENTS_REPO="jsolly/dotagents"

has_package_installer() {
  [[ -n "$1" && -f "$1/$PACKAGE_INSTALLER" ]]
}

clone_tmp=""
cleanup() {
  if [[ -n "$clone_tmp" ]]; then
    rm -rf "$clone_tmp"
  fi
}
trap cleanup EXIT

resolve_root() {
  local script_dir
  if has_package_installer "${DOTAGENTS_ROOT:-}"; then
    printf '%s\n' "$(cd "$DOTAGENTS_ROOT" && pwd)"
    return 0
  fi
  if [[ -n "${DOTAGENTS_ROOT:-}" ]]; then
    echo "cloud-package: WARN — ignoring DOTAGENTS_ROOT=$DOTAGENTS_ROOT: it has no $PACKAGE_INSTALLER" >&2
  fi
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ "$script_dir" == */templates/cloud-agent ]] && has_package_installer "${script_dir%/templates/cloud-agent}"; then
    printf '%s\n' "${script_dir%/templates/cloud-agent}"
    return 0
  fi
  if has_package_installer "${HOME}/code/dotagents"; then
    printf '%s\n' "$(cd "${HOME}/code/dotagents" && pwd)"
    return 0
  fi
  return 1
}

# Each fetcher reports only whether its fetch worked; what the tree holds is checked once, after.
fetch_via_gh_tarball() {
  local ref="$1" dest="$2" tarball
  command -v gh >/dev/null 2>&1 || return 1
  echo "cloud-package: fetching ${DOTAGENTS_REPO}@${ref} via gh api tarball"
  rm -rf "$dest"
  mkdir -p "$dest"
  tarball="$(mktemp "${clone_tmp}/tarball.XXXXXX")"
  if ! GH_PAGER=cat gh api "repos/${DOTAGENTS_REPO}/tarball/${ref}" >"$tarball"; then
    echo "cloud-package: gh api tarball failed for ${DOTAGENTS_REPO}@${ref}"
    return 1
  fi
  if [[ ! -s "$tarball" ]]; then
    echo "cloud-package: gh api tarball returned an empty body"
    return 1
  fi
  # GitHub tarballs unpack to a single {owner}-{repo}-{sha}/ prefix; drop it.
  tar -xzf "$tarball" -C "$dest" --strip-components=1
}

fetch_via_gh_repo_clone() {
  local ref="$1" dest="$2"
  command -v gh >/dev/null 2>&1 || return 1
  echo "cloud-package: cloning ${DOTAGENTS_REPO}@${ref} via gh repo clone (shallow)"
  rm -rf "$dest"
  GH_PAGER=cat gh repo clone "$DOTAGENTS_REPO" "$dest" -- --depth 1 --branch "$ref"
}

fetch_via_git_clone() {
  local ref="$1" dest="$2"
  echo "cloud-package: cloning ${DOTAGENTS_REPO}@${ref} via git clone (shallow)"
  rm -rf "$dest"
  GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=true git clone --depth 1 --branch "$ref" "https://github.com/${DOTAGENTS_REPO}.git" "$dest"
}

# Try gh's credentials first (tarball, then clone), then plain git clone.
fetch_checkout() {
  local ref="$1" dest="$2"
  fetch_via_gh_tarball "$ref" "$dest" || fetch_via_gh_repo_clone "$ref" "$dest" || fetch_via_git_clone "$ref" "$dest"
}

fetch_failed() {
  local ref="$1"
  echo "cloud-package: ERROR — could not fetch private dotagents (${DOTAGENTS_REPO}@${ref})." >&2
  echo "cloud-package: Set DOTAGENTS_ROOT to a checkout of jsolly/dotagents, or grant this environment git/gh access to that repo (GitHub App allowlist + environment.json repositoryDependencies: github.com/jsolly/dotagents). GitHub MCP read access is not git clone credentials. Do not vendor the private tree into this working copy." >&2
  exit 1
}

root=""
if root="$(resolve_root)"; then
  echo "cloud-package: using local checkout $root"
else
  clone_ref="${DOTAGENTS_CLONE_REF:-main}"
  clone_tmp="$(mktemp -d "${TMPDIR:-/tmp}/dotagents-cloud.XXXXXX")"
  root="$clone_tmp/dotagents"
  echo "cloud-package: no local checkout; fetching ${DOTAGENTS_REPO}@${clone_ref} (authenticated gh, then git clone)"
  fetch_checkout "$clone_ref" "$root" || fetch_failed "$clone_ref"
  if ! has_package_installer "$root"; then
    echo "cloud-package: ERROR — ${DOTAGENTS_REPO}@${clone_ref} has no ${PACKAGE_INSTALLER}: that ref predates this bootstrap. Fetch current main (unset DOTAGENTS_CLONE_REF)." >&2
    exit 1
  fi
fi

# Not exec: the EXIT trap still removes a fetched checkout once the installer returns.
"$BASH" "$root/$PACKAGE_INSTALLER"
