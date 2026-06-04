#!/usr/bin/env bash
# Assert .agents/FLEET.lock matches dotagents fleet branch when .agents/ changes.
# Ships in the fleet bundle at .agents/scripts/fleet-lock-check.sh and auto-propagates.
#
# Used by .github/workflows/fleet-lock-guard.yml after checkout:
#   - run: bash .agents/scripts/fleet-lock-check.sh
#     env:
#       FLEET_SYNC_TOKEN: ${{ secrets.FLEET_SYNC_TOKEN }}

set -euo pipefail

changed_files() {
  if [ -n "${GITHUB_BASE_REF:-}" ]; then
    if git fetch origin "$GITHUB_BASE_REF" --quiet 2>/dev/null; then
      git diff --name-only "origin/${GITHUB_BASE_REF}...HEAD" 2>/dev/null && return 0
    else
      echo "::warning::failed to fetch origin/${GITHUB_BASE_REF}; falling back to local comparison" >&2
    fi
  fi

  if [ -n "${GITHUB_EVENT_BEFORE:-}" ] && ! printf '%s' "$GITHUB_EVENT_BEFORE" | grep -qE '^0+$'; then
    git diff --name-only "$GITHUB_EVENT_BEFORE...HEAD" 2>/dev/null && return 0
  fi

  if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
    git diff --name-only "HEAD^...HEAD"
  else
    git ls-tree -r --name-only HEAD
  fi
}

if ! changed_files | grep -q '^\.agents/'; then
  echo "No .agents/ changes — lock check skipped"
  exit 0
fi

if [ -z "${FLEET_SYNC_TOKEN:-}" ]; then
  echo "::error::.agents/ changed but FLEET_SYNC_TOKEN is not set; cannot verify dotagents fleet lock"
  exit 1
fi

if [ ! -f .agents/FLEET.lock ]; then
  echo "::error::.agents/ changed but .agents/FLEET.lock is missing"
  exit 1
fi

LOCK_SHA="$(awk '/^sha:/ {print $2; exit}' .agents/FLEET.lock)"
if [ -z "$LOCK_SHA" ]; then
  echo "::error::.agents/FLEET.lock has no sha field"
  exit 1
fi

token="$(printf '%s' "$FLEET_SYNC_TOKEN" | tr -d '\n\r')"
FLEET_URL="https://x-access-token:${token}@github.com/jsolly/dotagents.git"
FLEET_HEAD="$(git ls-remote "$FLEET_URL" refs/heads/fleet | awk '{print $1}')"

if [ -z "$FLEET_HEAD" ]; then
  echo "::error::dotagents fleet branch not found — check FLEET_SYNC_TOKEN and repo access"
  exit 1
fi

if [ "$LOCK_SHA" != "$FLEET_HEAD" ]; then
  echo "::error::FLEET.lock sha ($LOCK_SHA) does not match dotagents fleet HEAD ($FLEET_HEAD)"
  exit 1
fi

echo "FLEET.lock matches dotagents fleet @ ${FLEET_HEAD:0:7}"

if ! git fetch "$FLEET_URL" "+refs/heads/fleet:refs/remotes/dotagents-fleet-lock/fleet" --quiet; then
  echo "::error::Failed to fetch dotagents fleet branch — check FLEET_SYNC_TOKEN and repo access"
  exit 1
fi

tmp_fleet="$(mktemp)"
tmp_child="$(mktemp)"
cleanup() {
  rm -f "$tmp_fleet" "$tmp_child"
}
trap cleanup EXIT

git ls-tree -r "$LOCK_SHA" | awk '$4 != "FLEET.lock" {print $4, $3}' | LC_ALL=C sort >"$tmp_fleet"
git ls-tree -r "HEAD:.agents" | awk '$4 != "FLEET.lock" {print $4, $3}' | LC_ALL=C sort >"$tmp_child"

if ! diff -q "$tmp_fleet" "$tmp_child" >/dev/null 2>&1; then
  echo "::error::.agents/ content does not match dotagents fleet @ ${LOCK_SHA:0:7}. Direct edits are clobbered on sync — change upstream in dotagents."
  echo "First differences (path blob):"
  diff "$tmp_fleet" "$tmp_child" | head -30 || true
  exit 1
fi

echo ".agents/ content matches dotagents fleet @ ${LOCK_SHA:0:7}"
