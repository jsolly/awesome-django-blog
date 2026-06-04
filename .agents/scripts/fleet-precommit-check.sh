#!/usr/bin/env bash
# Pre-commit guard: fail when .agents/FLEET.lock is behind dotagents/fleet.
# Read-only — does not run subtree pull or modify the working tree.
# Ships in the bundle at .agents/scripts/fleet-precommit-check.sh and auto-propagates.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

LOCK=".agents/FLEET.lock"
REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"

if [[ ! -f "$LOCK" ]]; then
  echo "Fleet pre-commit: no $LOCK — skipping fleet freshness check"
  exit 0
fi

LOCK_SHA="$(grep '^sha:' "$LOCK" | awk '{print $2}')"
if [[ -z "$LOCK_SHA" ]]; then
  echo "Fleet pre-commit: invalid $LOCK (missing sha field)" >&2
  exit 1
fi

if [[ -n "${DOTAGENTS_GITHUB_TOKEN:-}" ]]; then
  URL="https://x-access-token:${DOTAGENTS_GITHUB_TOKEN}@github.com/jsolly/dotagents.git"
elif [[ -n "${DOTAGENTS_URL:-}" ]]; then
  URL="$DOTAGENTS_URL"
else
  URL="git@github.com:jsolly/dotagents.git"
fi

if git remote get-url "$REMOTE" &>/dev/null; then
  if [[ -n "${DOTAGENTS_GITHUB_TOKEN:-}" || -n "${DOTAGENTS_URL:-}" ]]; then
    git remote set-url "$REMOTE" "$URL"
  fi
else
  git remote add "$REMOTE" "$URL"
fi

if ! git fetch "$REMOTE" "$BRANCH" --quiet 2>/dev/null; then
  echo "Fleet pre-commit: could not fetch ${REMOTE}/${BRANCH} — check network and dotagents access" >&2
  exit 1
fi

REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}^{commit}")"

if [[ "$LOCK_SHA" == "$REMOTE_SHA" ]]; then
  exit 0
fi

echo "Fleet pre-commit: .agents/FLEET.lock is stale (lock ${LOCK_SHA:0:7}, fleet ${REMOTE_SHA:0:7})" >&2
echo "Run ./scripts/update-agents-subtree.sh, review the generated sync commit, then retry your commit." >&2
exit 1
