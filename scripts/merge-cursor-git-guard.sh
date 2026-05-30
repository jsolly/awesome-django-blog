#!/usr/bin/env bash
# Merge fleet git --no-verify guard into .cursor/hooks.json (idempotent).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

GUARD=".agents/hooks/block-git-no-verify.sh"
[[ -x "$GUARD" ]] || { echo "Missing $GUARD — run subtree pull first" >&2; exit 1; }

HOOKS=".cursor/hooks.json"
mkdir -p .cursor
if [[ -f "$HOOKS" ]]; then
  jq --arg cmd "bash $GUARD" '
    .version //= 1
    | .hooks.beforeShellExecution //= []
    | if (.hooks.beforeShellExecution | map(.command // "") | any(test("block-git-no-verify"))) then .
      else .hooks.beforeShellExecution += [{command: $cmd, failClosed: true, timeout: 5}]
      end
  ' "$HOOKS" > "$HOOKS.new"
else
  jq -n --arg cmd "bash $GUARD" '{
    version: 1,
    hooks: { beforeShellExecution: [{ command: $cmd, failClosed: true, timeout: 5 }] }
  }' > "$HOOKS.new"
fi
mv "$HOOKS.new" "$HOOKS"
echo "Merged git guard into $HOOKS"
