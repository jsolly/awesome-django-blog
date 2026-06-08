#!/usr/bin/env bash
# Merge both fleet Cursor hooks into .cursor/hooks.json in one pass (idempotent):
#   - git --no-verify guard  -> beforeShellExecution (block-git-no-verify.sh, failClosed)
#   - fleet edit guard       -> preToolUse (block-fleet-edits.sh, Write|Delete)
# Replaces merge-cursor-git-guard.sh + merge-cursor-edit-guard.sh. Ships in the bundle at
# .agents/scripts/merge-cursor-hooks.sh and auto-propagates. Also strips deprecated
# sessionStart fleet stale-check entries if present.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

GIT_GUARD=".agents/hooks/block-git-no-verify.sh"
EDIT_GUARD=".agents/hooks/block-fleet-edits.sh"
[[ -x "$GIT_GUARD" ]] || { echo "Missing $GIT_GUARD — run subtree pull first" >&2; exit 1; }
[[ -x "$EDIT_GUARD" ]] || { echo "Missing $EDIT_GUARD — run subtree pull first" >&2; exit 1; }

HOOKS=".cursor/hooks.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p .cursor

merge_hooks() {
  jq --arg git_cmd "bash $GIT_GUARD" --arg edit_cmd "bash $EDIT_GUARD" '
    .version //= 1
    # git --no-verify guard (beforeShellExecution): append once if absent.
    | .hooks.beforeShellExecution //= []
    | if (.hooks.beforeShellExecution | map(.command // "") | any(test("block-git-no-verify"))) then .
      else .hooks.beforeShellExecution += [{command: $git_cmd, failClosed: true, timeout: 5}]
      end
    # Strip deprecated sessionStart fleet stale-check entries.
    | .hooks.sessionStart = ((.hooks.sessionStart // [])
        | map(select((.command // "") | test("check-fleet-subtree-stale") | not)))
    | if (.hooks.sessionStart | length) == 0 then del(.hooks.sessionStart) else . end
    # Fleet edit guard (preToolUse): refresh existing entry, else append once.
    | .hooks.preToolUse //= []
    | .hooks.preToolUse |= map(
        if ((.command // "") | test("block-fleet-edits"))
        then . + {command: $edit_cmd, failClosed: false, timeout: 5, matcher: "Write|Delete"}
        else .
        end
      )
    | if (.hooks.preToolUse | map(.command // "") | any(test("block-fleet-edits"))) then .
      else .hooks.preToolUse += [{
        command: $edit_cmd,
        failClosed: false,
        timeout: 5,
        matcher: "Write|Delete"
      }]
      end
  '
}

if [[ -f "$HOOKS" ]]; then
  merge_hooks <"$HOOKS" >"$HOOKS.new"
else
  merge_hooks <<<'{"version":1,"hooks":{}}' >"$HOOKS.new"
fi
mv "$HOOKS.new" "$HOOKS"
bash "$SCRIPT_DIR/format-repo-json.sh" "$HOOKS" || true
echo "Merged git + fleet edit guards into $HOOKS"
