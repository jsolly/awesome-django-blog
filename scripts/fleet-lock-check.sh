#!/usr/bin/env bash
# Assert .agents/FLEET.lock matches dotagents fleet branch when .agents/ changes in a PR.
# Ships in the fleet bundle at .agents/scripts/fleet-lock-check.sh and auto-propagates.
#
# Used by .github/workflows/fleet-lock-guard.yml (after checkout, when FLEET_SYNC_TOKEN is set):
#   - run: bash .agents/scripts/fleet-lock-check.sh
#     env:
#       FLEET_SYNC_TOKEN: ${{ secrets.FLEET_SYNC_TOKEN }}

set -euo pipefail

if ! git diff --name-only "origin/${GITHUB_BASE_REF:-main}...HEAD" | grep -q '^\.agents/'; then
  echo "No .agents/ changes — lock check skipped"
  exit 0
fi

if [ -z "${FLEET_SYNC_TOKEN:-}" ]; then
  echo "::warning::FLEET_SYNC_TOKEN not set — skipping FLEET.lock check"
  exit 0
fi

if [ ! -f .agents/FLEET.lock ]; then
  echo "::error::.agents/ changed but .agents/FLEET.lock is missing"
  exit 1
fi

LOCK_SHA="$(grep '^sha:' .agents/FLEET.lock | awk '{print $2}')"
if [ -z "$LOCK_SHA" ]; then
  echo "::error::.agents/FLEET.lock has no sha field"
  exit 1
fi

git remote remove dotagents-lock 2>/dev/null || true
git remote add dotagents-lock "https://x-access-token:${FLEET_SYNC_TOKEN}@github.com/jsolly/dotagents.git"
FLEET_HEAD="$(git ls-remote dotagents-lock refs/heads/fleet | awk '{print $1}')"

if [ "$LOCK_SHA" != "$FLEET_HEAD" ]; then
  echo "::error::FLEET.lock sha ($LOCK_SHA) does not match dotagents fleet HEAD ($FLEET_HEAD)"
  exit 1
fi

echo "FLEET.lock matches dotagents fleet @ ${FLEET_HEAD:0:7}"

if ! git fetch dotagents-lock fleet --quiet; then
  echo "::error::Failed to fetch dotagents fleet branch — check FLEET_SYNC_TOKEN and repo access"
  exit 1
fi

tmp_fleet="$(mktemp)"
tmp_child="$(mktemp)"
cleanup() {
  rm -f "$tmp_fleet" "$tmp_child"
  git remote remove dotagents-lock 2>/dev/null || true
}
trap cleanup EXIT

git ls-tree -r "$LOCK_SHA" | awk '{print $4, $3}' | LC_ALL=C sort >"$tmp_fleet"
git ls-tree -r "HEAD:.agents" | awk '$4 != "FLEET.lock" {print $4, $3}' | LC_ALL=C sort >"$tmp_child"

if ! diff -q "$tmp_fleet" "$tmp_child" >/dev/null 2>&1; then
  echo "::error::.agents/ content does not match dotagents fleet @ ${LOCK_SHA:0:7}. Direct edits are clobbered on sync — change upstream in dotagents."
  echo "First differences (path blob):"
  diff "$tmp_fleet" "$tmp_child" | head -30 || true
  exit 1
fi

echo ".agents/ content matches dotagents fleet @ ${LOCK_SHA:0:7}"
