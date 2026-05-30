#!/usr/bin/env bash
# Pull latest fleet config from dotagents into .agents/, then relink Cursor rules.
# Run from repo root.
#
# .agents/ is read-only (pull-only). The dotagents `fleet` branch is published by CI
# from ~/.agents/ — make fleet changes there, not here. Pushing .agents/ edits back
# upstream does not round-trip; the next CI publish overwrites the branch.

set -euo pipefail

REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"

if ! git remote get-url "$REMOTE" &>/dev/null; then
  git remote add "$REMOTE" git@github.com:jsolly/dotagents.git
fi

git fetch "$REMOTE" "$BRANCH"
git subtree pull --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Update agent fleet subtree" || \
  git subtree add --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Add agent fleet subtree from dotagents"

# Project-local .agents/hooks and .agents/automations are NOT in the fleet branch — subtree pull will not remove them if committed here.
bash .agents/scripts/link-fleet-rules.sh

echo "Updated .agents/ from ${REMOTE}/${BRANCH}"
