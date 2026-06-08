#!/usr/bin/env bash
# Merge fleet edit guard into .cursor/hooks.json (idempotent).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

GUARD=".agents/hooks/block-fleet-edits.sh"
[[ -x "$GUARD" ]] || { echo "Missing $GUARD — run subtree pull first" >&2; exit 1; }

HOOKS=".cursor/hooks.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p .cursor

merge_hooks() {
	jq --arg guard_cmd "bash $GUARD" '
		.version //= 1
		| .hooks.preToolUse //= []
		| .hooks.preToolUse |= map(
				if ((.command // "") | test("block-fleet-edits"))
				then . + {command: $guard_cmd, failClosed: false, timeout: 5, matcher: "Write|Delete"}
				else .
				end
			)
		| if (.hooks.preToolUse | map(.command // "") | any(test("block-fleet-edits"))) then .
			else .hooks.preToolUse += [{
				command: $guard_cmd,
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
	merge_hooks <<< '{"version":1,"hooks":{}}' >"$HOOKS.new"
fi
mv "$HOOKS.new" "$HOOKS"
bash "$SCRIPT_DIR/format-repo-json.sh" "$HOOKS" || true
echo "Merged fleet edit guard into $HOOKS"
