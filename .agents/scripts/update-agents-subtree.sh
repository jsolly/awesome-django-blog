#!/usr/bin/env bash
# Fleet subtree updater. Ships in the bundle at .agents/scripts/update-agents-subtree.sh and
# auto-propagates. Pulls dotagents/fleet into .agents/, writes FLEET.lock, then converges
# repo shape. Invoked via the repo's thin scripts/update-agents-subtree.sh shim, which runs
# this from a temp copy so the subtree pull cannot overwrite the executing script mid-run.
#
# .agents/ is read-only (pull-only). The fleet branch is published by CI from the dotagents
# repo; edits to .agents/ here do not round-trip — make fleet changes upstream in dotagents.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"

if [ -n "${DOTAGENTS_GITHUB_TOKEN:-}" ]; then
  URL="https://x-access-token:${DOTAGENTS_GITHUB_TOKEN}@github.com/jsolly/dotagents.git"
else
  URL="${DOTAGENTS_URL:-git@github.com:jsolly/dotagents.git}"
fi

if git remote get-url "$REMOTE" &>/dev/null; then
  git remote set-url "$REMOTE" "$URL"
else
  git remote add "$REMOTE" "$URL"
fi

git fetch "$REMOTE" "$BRANCH"
REMOTE_SHA="$(git rev-parse "${REMOTE}/${BRANCH}^{commit}")"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree must be clean before fleet subtree pull (commit or stash first)." >&2
  exit 1
fi

if [[ -f .agents/FLEET.lock ]]; then
  LOCK_SHA="$(grep '^sha:' .agents/FLEET.lock | awk '{print $2}')"
  if [[ -n "$LOCK_SHA" && "$LOCK_SHA" == "$REMOTE_SHA" ]]; then
    echo "Fleet already at ${REMOTE}/${BRANCH} (${REMOTE_SHA:0:7}) — converging shape only"
    bash .agents/scripts/converge-repo.sh
    git add -A
    git diff --cached --quiet || git commit -m "chore(fleet): converge agent fleet shape"
    exit 0
  fi
  git rm -f .agents/FLEET.lock
  git commit -m "chore(fleet): remove stale FLEET.lock before subtree pull"
fi

git subtree pull --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Update agent fleet subtree" || \
  git subtree add --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Add agent fleet subtree from dotagents"

printf 'sha: %s\n' "$REMOTE_SHA" > .agents/FLEET.lock

# Post-pull shape convergence (rule links, git guard, workflow ref, stale-file cleanup).
bash .agents/scripts/converge-repo.sh

git add -A
git diff --cached --quiet || git commit -m "chore(fleet): sync agent fleet from dotagents"

echo "Updated .agents/ from ${REMOTE}/${BRANCH} (FLEET.lock: ${REMOTE_SHA:0:7})"
