#!/usr/bin/env bash
# Merge fleet git --no-verify guard into .cursor/hooks.json (idempotent).
# Strips deprecated sessionStart fleet stale-check entries if present.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

GUARD=".agents/hooks/block-git-no-verify.sh"
[[ -x "$GUARD" ]] || { echo "Missing $GUARD — run subtree pull first" >&2; exit 1; }

HOOKS=".cursor/hooks.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p .cursor

merge_hooks() {
  jq --arg guard_cmd "bash $GUARD" '
    .version //= 1
    | .hooks.beforeShellExecution //= []
    | if (.hooks.beforeShellExecution | map(.command // "") | any(test("block-git-no-verify"))) then .
      else .hooks.beforeShellExecution += [{command: $guard_cmd, failClosed: true, timeout: 5}]
      end
    | .hooks.sessionStart = ((.hooks.sessionStart // [])
        | map(select((.command // "") | test("check-fleet-subtree-stale") | not)))
    | if (.hooks.sessionStart | length) == 0 then del(.hooks.sessionStart) else . end
  '
}

if [[ -f "$HOOKS" ]]; then
  merge_hooks < "$HOOKS" > "$HOOKS.new"
else
  merge_hooks <<< '{"version":1,"hooks":{}}' > "$HOOKS.new"
fi
mv "$HOOKS.new" "$HOOKS"
bash "$SCRIPT_DIR/format-repo-json.sh" "$HOOKS" || true
echo "Merged git guard into $HOOKS"
