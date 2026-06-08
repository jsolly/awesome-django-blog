#!/usr/bin/env bash
# Shared helpers for talking to the dotagents fleet git remote. Ships in the bundle at
# .agents/scripts/fleet-remote.sh and auto-propagates. Meant to be *sourced*, not run.
#
# Sourced by fleet-precommit-check.sh and update-agents-subtree.sh — scripts that resolve
# the dotagents URL, point a git remote at it, fetch the fleet branch, and compare the
# fetched sha to FLEET.lock. (cloud-fleet-sync-if-stale.sh keeps its own inline copy so the
# cloud-boot path has no sourcing dependency.)
#
# NOT used by fleet-lock-check.sh: that one talks to the GitHub REST API (curl + jq),
# not a git remote, so it stays independent.
#
# Callers must already have `set -euo pipefail` and define $ROOT (the repo toplevel)
# before sourcing — fleet_set_remote/fleet_fetch/fleet_remote_sha operate on $ROOT's repo.

# Remote name + branch, overridable via env (defaults match every shim and caller).
fleet_remote_name() { printf '%s' "${DOTAGENTS_REMOTE:-dotagents}"; }
fleet_remote_branch() { printf '%s' "${DOTAGENTS_BRANCH:-fleet}"; }

# Resolve the dotagents URL: FLEET_SYNC_TOKEN (CI/cloud) > DOTAGENTS_URL (override/tests) > SSH.
fleet_remote_url() {
  if [[ -n "${FLEET_SYNC_TOKEN:-}" ]]; then
    printf '%s' "https://x-access-token:${FLEET_SYNC_TOKEN}@github.com/jsolly/dotagents.git"
  else
    printf '%s' "${DOTAGENTS_URL:-git@github.com:jsolly/dotagents.git}"
  fi
}

# Ensure the dotagents remote exists and points at the resolved URL.
#   fleet_set_remote            -> always refresh an existing remote's URL (sync/pull callers)
#   fleet_set_remote preserve   -> leave an existing remote's URL alone unless FLEET_SYNC_TOKEN
#                                  or DOTAGENTS_URL is set (the read-only pre-commit check must
#                                  not clobber a repo's configured dotagents remote)
fleet_set_remote() {
  local mode="${1:-refresh}"
  local remote url
  remote="$(fleet_remote_name)"
  url="$(fleet_remote_url)"
  if git remote get-url "$remote" &>/dev/null; then
    if [[ "$mode" != "preserve" || -n "${FLEET_SYNC_TOKEN:-}" || -n "${DOTAGENTS_URL:-}" ]]; then
      git remote set-url "$remote" "$url"
    fi
  else
    git remote add "$remote" "$url"
  fi
}

# Fetch the fleet branch quietly. Returns git's exit status so callers can choose their
# own error message (or rely on `set -e`).
fleet_fetch() {
  git fetch "$(fleet_remote_name)" "$(fleet_remote_branch)" --quiet
}

# Print the fetched fleet branch HEAD commit sha.
fleet_remote_sha() {
  git rev-parse "$(fleet_remote_name)/$(fleet_remote_branch)^{commit}"
}

# Print the sha recorded in a FLEET.lock file (default: .agents/FLEET.lock). Empty when absent.
fleet_lock_sha() {
  local lock="${1:-.agents/FLEET.lock}"
  [[ -f "$lock" ]] || return 0
  awk '/^sha:/ {print $2; exit}' "$lock"
}
