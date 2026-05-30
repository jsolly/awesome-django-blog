#!/usr/bin/env bash
# Block edits to fleet-managed paths (Cursor preToolUse hook).
# Fail-open on parse errors so a hook bug cannot block all editing.
set -uo pipefail

input=$(cat 2>/dev/null || true)

allow() {
	echo '{"permission":"allow"}'
	exit 0
}

deny() {
	local msg="$1"
	jq -n --arg um "$msg" --arg am "$msg" '{
		permission: "deny",
		user_message: $um,
		agent_message: $am
	}'
	exit 0
}

[[ -n "$input" ]] || allow

if ! printf '%s' "$input" | jq -e . >/dev/null 2>&1; then
	allow
fi

file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.path // .tool_input.target_file // ""')
cwd=$(printf '%s' "$input" | jq -r '.cwd // ""')

[[ -n "$file_path" ]] || allow

root=""
if [[ -n "$cwd" ]]; then
	root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || true)"
fi
[[ -n "$root" ]] || root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[[ -n "$root" ]] || root="$cwd"
[[ -n "$root" ]] || allow

rel_path=$(python3 - "$root" "$cwd" "$file_path" <<'PY'
import os
import sys

root, cwd, fp = sys.argv[1], sys.argv[2], sys.argv[3]
if os.path.isabs(fp):
	path = os.path.normpath(fp)
else:
	base = cwd if cwd else root
	path = os.path.normpath(os.path.join(base, fp))
path = os.path.realpath(path)
root = os.path.realpath(os.path.normpath(root))
try:
	rel = os.path.relpath(path, root)
except ValueError:
	sys.exit(0)
if rel.startswith(".."):
	sys.exit(0)
print(rel.replace("\\", "/"), end="")
PY
)

[[ -n "$rel_path" ]] || allow

block_msg='This path is fleet-managed and read-only in app repos. Edit upstream in dotagents (~/code/dotagents), push to main, then sync via scripts/update-agents-subtree.sh.'

case "$rel_path" in
.agents | .agents/*)
	deny "$block_msg"
	;;
esac

case "$rel_path" in
scripts/update-agents-subtree.sh | scripts/cloud-fleet-sync-if-stale.sh | .github/workflows/fleet-lock-guard.yml)
	deny "$block_msg"
	;;
esac

allow
