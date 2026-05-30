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
    echo "Fleet already at ${REMOTE}/${BRANCH} (${REMOTE_SHA:0:7})"
    bash .agents/scripts/link-fleet-rules.sh
    if [[ -x .agents/scripts/merge-cursor-git-guard.sh ]]; then
      bash .agents/scripts/merge-cursor-git-guard.sh
    fi
    exit 0
  fi
  git rm -f .agents/FLEET.lock
  git commit -m "chore(fleet): remove stale FLEET.lock before subtree pull"
fi

git subtree pull --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Update agent fleet subtree" || \
  git subtree add --prefix=.agents "$REMOTE" "$BRANCH" --squash -m "Add agent fleet subtree from dotagents"

printf 'sha: %s\n' "$REMOTE_SHA" > .agents/FLEET.lock

# Project-local .agents/hooks and .agents/automations are NOT in the fleet branch — subtree pull will not remove them if committed here.
bash .agents/scripts/link-fleet-rules.sh

if [[ -x .agents/scripts/merge-cursor-git-guard.sh ]]; then
  bash .agents/scripts/merge-cursor-git-guard.sh
fi

if [[ -f .agents/docs/cloud-agents.md ]]; then
  cp .agents/docs/cloud-agents.md docs/cloud-agents.md
  if [[ "$(uname -s)" == Darwin ]]; then
    sed -i '' "s/# Cursor Cloud Agents/# Cursor Cloud Agents — $(basename "$PWD")/" docs/cloud-agents.md
  else
    sed -i "s/# Cursor Cloud Agents/# Cursor Cloud Agents — $(basename "$PWD")/" docs/cloud-agents.md
  fi
fi

if [[ -n "$(git status --porcelain)" ]]; then
  git add .agents/FLEET.lock .cursor/hooks.json .cursor/rules docs/cloud-agents.md 2>/dev/null || true
  git add -u .agents 2>/dev/null || true
  if ! git diff --cached --quiet 2>/dev/null; then
    git commit -m "chore(fleet): sync agent fleet from dotagents"
  fi
fi

echo "Updated .agents/ from ${REMOTE}/${BRANCH} (FLEET.lock: ${REMOTE_SHA:0:7})"
