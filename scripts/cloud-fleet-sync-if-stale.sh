#!/usr/bin/env bash
# Cloud task startup: pull fleet subtree when FLEET.lock is behind dotagents/fleet.
# Requires DOTAGENTS_GITHUB_TOKEN (or SSH dotagents remote) and a clean working tree.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

LOCK=".agents/FLEET.lock"
REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"

if [[ ! -f "$LOCK" ]]; then
  echo "Missing $LOCK — run ./scripts/update-agents-subtree.sh first" >&2
  exit 1
fi

LOCK_SHA="$(grep '^sha:' "$LOCK" | awk '{print $2}')"
[[ -n "$LOCK_SHA" ]] || { echo "Invalid $LOCK" >&2; exit 1; }

git remote get-url "$REMOTE" &>/dev/null || {
  echo "Missing git remote $REMOTE — run ./scripts/update-agents-subtree.sh" >&2
  exit 1
}

git fetch "$REMOTE" "$BRANCH" --quiet
REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}^{commit}")"

if [[ "$LOCK_SHA" == "$REMOTE_SHA" ]]; then
  echo "Fleet already at ${REMOTE}/${BRANCH} (${REMOTE_SHA:0:7})"
  exit 0
fi

echo "Fleet stale (lock ${LOCK_SHA:0:7}, remote ${REMOTE_SHA:0:7}) — running ./scripts/update-agents-subtree.sh" >&2
./scripts/update-agents-subtree.sh
