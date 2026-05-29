#!/usr/bin/env bash
# Pull latest fleet config from dotagents into .agents/, then relink Cursor rules.
# Run from repo root.
#
# Push local .agents/ edits back to dotagents:
#   git subtree push --prefix=.agents dotagents fleet
# Then merge origin/fleet into dotagents main fleet/ (or re-run refresh-fleet there).

set -euo pipefail

REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"

if ! git remote get-url "$REMOTE" &>/dev/null; then
  git remote add "$REMOTE" git@github.com:jsolly/dotagents.git
fi

git fetch "$REMOTE" "$BRANCH"
git subtree pull --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Update agent fleet subtree" || \
  git subtree add --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Add agent fleet subtree from dotagents"

./scripts/link-fleet-rules.sh

echo "Updated .agents/ from ${REMOTE}/${BRANCH}"
