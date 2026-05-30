#!/usr/bin/env bash
# Cloud task startup: pull the fleet subtree when FLEET.lock is behind dotagents/fleet.
# Ships in the bundle at .agents/scripts/cloud-fleet-sync-if-stale.sh and auto-propagates.
# Invoked via the repo's thin scripts/cloud-fleet-sync-if-stale.sh shim.
# Requires DOTAGENTS_GITHUB_TOKEN (or an SSH dotagents remote) and a clean working tree.
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

if [[ -n "${DOTAGENTS_GITHUB_TOKEN:-}" ]]; then
  URL="https://x-access-token:${DOTAGENTS_GITHUB_TOKEN}@github.com/jsolly/dotagents.git"
elif [[ -n "${DOTAGENTS_URL:-}" ]]; then
  URL="$DOTAGENTS_URL"
else
  URL="git@github.com:jsolly/dotagents.git"
fi

if git remote get-url "$REMOTE" &>/dev/null; then
  git remote set-url "$REMOTE" "$URL"
else
  git remote add "$REMOTE" "$URL"
fi

git fetch "$REMOTE" "$BRANCH" --quiet
REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}^{commit}")"

if [[ "$LOCK_SHA" == "$REMOTE_SHA" ]]; then
  echo "Fleet already at ${REMOTE}/${BRANCH} (${REMOTE_SHA:0:7})"
  exit 0
fi

echo "Fleet stale (lock ${LOCK_SHA:0:7}, remote ${REMOTE_SHA:0:7}) — running ./scripts/update-agents-subtree.sh" >&2
exec ./scripts/update-agents-subtree.sh
