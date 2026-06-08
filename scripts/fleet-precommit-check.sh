#!/usr/bin/env bash
# Pre-commit guard: fail when .agents/FLEET.lock is behind dotagents/fleet.
# Read-only — does not run subtree pull or modify the working tree.
# Ships in the bundle at .agents/scripts/fleet-precommit-check.sh and auto-propagates.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# Runs in-place from .agents/scripts (not a temp copy), so the sibling lib is always present.
# shellcheck source=/dev/null
source "$(dirname "${BASH_SOURCE[0]}")/fleet-remote.sh"

LOCK=".agents/FLEET.lock"
REMOTE="$(fleet_remote_name)"
BRANCH="$(fleet_remote_branch)"

if [[ ! -f "$LOCK" ]]; then
  echo "Fleet pre-commit: no $LOCK — skipping fleet freshness check"
  exit 0
fi

LOCK_SHA="$(fleet_lock_sha "$LOCK")"
if [[ -z "$LOCK_SHA" ]]; then
  echo "Fleet pre-commit: invalid $LOCK (missing sha field)" >&2
  exit 1
fi

# Read-only check: don't clobber a repo's configured dotagents remote URL.
fleet_set_remote preserve

if ! fleet_fetch 2>/dev/null; then
  echo "Fleet pre-commit: could not fetch ${REMOTE}/${BRANCH} — check network and dotagents access" >&2
  exit 1
fi

REMOTE_SHA="$(fleet_remote_sha)"

if [[ "$LOCK_SHA" == "$REMOTE_SHA" ]]; then
  exit 0
fi

echo "Fleet pre-commit: .agents/FLEET.lock is stale (lock ${LOCK_SHA:0:7}, fleet ${REMOTE_SHA:0:7})" >&2
echo "Run ./scripts/update-agents-subtree.sh, review the generated sync commit, then retry your commit." >&2
exit 1
