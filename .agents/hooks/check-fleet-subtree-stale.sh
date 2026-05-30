#!/usr/bin/env bash
# sessionStart: warn when .agents/FLEET.lock is behind dotagents fleet.
# Fail open on missing remote, network errors, or non-fleet repos.
set -euo pipefail

ROOT="${CURSOR_PROJECT_DIR:-}"
if [[ -z "$ROOT" ]]; then
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
cd "$ROOT"

LOCK=".agents/FLEET.lock"
[[ -f "$LOCK" ]] || exit 0

LOCK_SHA="$(grep '^sha:' "$LOCK" | awk '{print $2}')"
[[ -n "$LOCK_SHA" ]] || exit 0

REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"

git remote get-url "$REMOTE" &>/dev/null || exit 0

if ! git fetch "$REMOTE" "$BRANCH" --quiet 2>/dev/null; then
  exit 0
fi

REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}^{commit}" 2>/dev/null || true)"
[[ -n "$REMOTE_SHA" ]] || exit 0

if [[ "$LOCK_SHA" == "$REMOTE_SHA" ]]; then
  echo '{}'
  exit 0
fi

LOCK_SHORT="${LOCK_SHA:0:7}"
REMOTE_SHORT="${REMOTE_SHA:0:7}"

context="Fleet subtree is behind dotagents: FLEET.lock is ${LOCK_SHORT}, ${REMOTE}/${BRANCH} is ${REMOTE_SHORT}. Before fleet-dependent work, run ./scripts/update-agents-subtree.sh from the repo root (ask the user before running git commands)."

jq -n \
  --arg context "$context" \
  --arg lock "$LOCK_SHA" \
  --arg remote "$REMOTE_SHA" \
  '{
    additional_context: $context,
    env: {
      FLEET_SUBTREE_STALE: "1",
      FLEET_LOCK_SHA: $lock,
      FLEET_REMOTE_SHA: $remote
    }
  }'
