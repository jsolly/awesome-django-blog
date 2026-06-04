#!/usr/bin/env bash
# Assert .agents/FLEET.lock matches dotagents fleet branch when .agents/ changes.
# Ships in the fleet bundle at .agents/scripts/fleet-lock-check.sh and auto-propagates.
#
# Used by .github/workflows/fleet-lock-guard.yml after checkout:
#   - run: bash .agents/scripts/fleet-lock-check.sh
#     env:
#       FLEET_SYNC_TOKEN: ${{ secrets.FLEET_SYNC_TOKEN }}

set -euo pipefail

DOTAGENTS_REPO="${DOTAGENTS_REPO:-jsolly/dotagents}"
DOTAGENTS_BRANCH="${DOTAGENTS_BRANCH:-fleet}"

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

github_api() {
  local path="$1"
  curl -sf -H "Authorization: Bearer ${token}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com${path}"
}

write_fleet_tree_list() {
  local commit_sha="$1"
  local out="$2"
  local tree_sha
  tree_sha="$(github_api "/repos/${DOTAGENTS_REPO}/commits/${commit_sha}" | jq -r '.commit.tree.sha')"
  if [ -z "$tree_sha" ] || [ "$tree_sha" = "null" ]; then
    echo "::error::Could not resolve dotagents tree for ${commit_sha:0:7}" >&2
    return 1
  fi
  github_api "/repos/${DOTAGENTS_REPO}/git/trees/${tree_sha}?recursive=1" \
    | jq -r '.tree[] | select(.type == "blob" and .path != "FLEET.lock") | "\(.path) \(.sha)"' \
    | LC_ALL=C sort >"$out"
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

if ! command -v curl >/dev/null || ! command -v jq >/dev/null; then
  echo "::error::fleet-lock-check requires curl and jq" >&2
  exit 1
fi

token="$(printf '%s' "$FLEET_SYNC_TOKEN" | tr -d '\n\r')"

if ! FLEET_HEAD="$(github_api "/repos/${DOTAGENTS_REPO}/commits/${DOTAGENTS_BRANCH}" | jq -r '.sha')"; then
  echo "::error::Could not read dotagents/${DOTAGENTS_BRANCH} — check FLEET_SYNC_TOKEN and repo access"
  exit 1
fi

if [ -z "$FLEET_HEAD" ] || [ "$FLEET_HEAD" = "null" ]; then
  echo "::error::dotagents ${DOTAGENTS_BRANCH} branch not found — check FLEET_SYNC_TOKEN and repo access"
  exit 1
fi

if [ "$LOCK_SHA" != "$FLEET_HEAD" ]; then
  echo "::error::FLEET.lock sha ($LOCK_SHA) does not match dotagents fleet HEAD ($FLEET_HEAD)"
  exit 1
fi

echo "FLEET.lock matches dotagents fleet @ ${FLEET_HEAD:0:7}"

tmp_fleet="$(mktemp)"
tmp_child="$(mktemp)"
cleanup() {
  rm -f "$tmp_fleet" "$tmp_child"
}
trap cleanup EXIT

if ! write_fleet_tree_list "$LOCK_SHA" "$tmp_fleet"; then
  exit 1
fi

git ls-tree -r "HEAD:.agents" | awk '$4 != "FLEET.lock" {print $4, $3}' | LC_ALL=C sort >"$tmp_child"

if ! diff -q "$tmp_fleet" "$tmp_child" >/dev/null 2>&1; then
  echo "::error::.agents/ content does not match dotagents fleet @ ${LOCK_SHA:0:7}. Direct edits are clobbered on sync — change upstream in dotagents."
  echo "First differences (path blob):"
  diff "$tmp_fleet" "$tmp_child" | head -30 || true
  exit 1
fi

echo ".agents/ content matches dotagents fleet @ ${LOCK_SHA:0:7}"
