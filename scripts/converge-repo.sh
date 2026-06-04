#!/usr/bin/env bash
# Idempotently converge a repo to the current fleet shape. Ships in the bundle at
# .agents/scripts/converge-repo.sh and auto-propagates. Safe to re-run. Does NOT commit
# (the caller — update-agents-subtree.sh or onboard-repo.sh — stages and commits).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# 1. Wire fleet rules into .cursor/rules and merge fleet guards.
[[ -x .agents/scripts/link-fleet-rules.sh ]] && bash .agents/scripts/link-fleet-rules.sh
[[ -x .agents/scripts/merge-cursor-git-guard.sh ]] && bash .agents/scripts/merge-cursor-git-guard.sh
[[ -x .agents/scripts/merge-cursor-edit-guard.sh ]] && bash .agents/scripts/merge-cursor-edit-guard.sh
[[ -x .agents/scripts/merge-claude-edit-guard.sh ]] && bash .agents/scripts/merge-claude-edit-guard.sh
[[ -x .agents/scripts/install-fleet-precommit-hook.sh ]] && bash .agents/scripts/install-fleet-precommit-hook.sh

# 2. The fleet-lock-guard workflow must call the bundled checker, not a vendored copy.
WF=".github/workflows/fleet-lock-guard.yml"
if [[ -f "$WF" ]] && grep -q '\.github/scripts/fleet-lock-check\.sh' "$WF"; then
  sed -i.bak 's#\.github/scripts/fleet-lock-check\.sh#.agents/scripts/fleet-lock-check.sh#g' "$WF"
  rm -f "$WF.bak"
fi

# 3. Drop the now-bundled vendored checker (logic lives in .agents/scripts/fleet-lock-check.sh).
rm -f .github/scripts/fleet-lock-check.sh
rmdir .github/scripts 2>/dev/null || true

# 4. cloud-agents doc is read from the subtree (.agents/docs/cloud-agents.md);
#    drop the duplicated, name-customized outer copy.
rm -f docs/cloud-agents.md

# 5. Repoint any AGENTS.md reference at the subtree copy (skip if already correct).
if [[ -f AGENTS.md ]] && grep -q 'docs/cloud-agents.md' AGENTS.md; then
  sed -i.bak 's#\([^/]\)docs/cloud-agents\.md#\1.agents/docs/cloud-agents.md#g' AGENTS.md
  rm -f AGENTS.md.bak
fi

echo "Converged repo shape at $ROOT"
