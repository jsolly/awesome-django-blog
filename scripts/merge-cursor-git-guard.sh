#!/usr/bin/env bash
# Merge fleet Cursor hooks into .cursor/hooks.json (idempotent).
# - beforeShellExecution: block git --no-verify
# - sessionStart: warn when FLEET.lock is behind dotagents fleet
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

GUARD=".agents/hooks/block-git-no-verify.sh"
STALE_CHECK=".agents/hooks/check-fleet-subtree-stale.sh"
[[ -x "$GUARD" ]] || { echo "Missing $GUARD — run subtree pull first" >&2; exit 1; }
[[ -x "$STALE_CHECK" ]] || { echo "Missing $STALE_CHECK — run subtree pull first" >&2; exit 1; }

HOOKS=".cursor/hooks.json"
mkdir -p .cursor

merge_hooks() {
  jq --arg guard_cmd "bash $GUARD" --arg session_cmd "bash $STALE_CHECK" '
    .version //= 1
    | .hooks.beforeShellExecution //= []
    | if (.hooks.beforeShellExecution | map(.command // "") | any(test("block-git-no-verify"))) then .
      else .hooks.beforeShellExecution += [{command: $guard_cmd, failClosed: true, timeout: 5}]
      end
    | .hooks.sessionStart //= []
    | if (.hooks.sessionStart | map(.command // "") | any(test("check-fleet-subtree-stale"))) then .
      else .hooks.sessionStart += [{command: $session_cmd, timeout: 15}]
      end
  '
}

if [[ -f "$HOOKS" ]]; then
  merge_hooks < "$HOOKS" > "$HOOKS.new"
else
  merge_hooks <<< '{"version":1,"hooks":{}}' > "$HOOKS.new"
fi
mv "$HOOKS.new" "$HOOKS"
echo "Merged fleet Cursor hooks into $HOOKS"
