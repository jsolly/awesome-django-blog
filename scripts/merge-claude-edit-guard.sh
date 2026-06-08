#!/usr/bin/env bash
# Merge fleet edit deny rules into .claude/settings.json (idempotent).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

FLEET_DENY=".agents/templates/claude-settings.json"
[[ -f "$FLEET_DENY" ]] || { echo "Missing $FLEET_DENY — run subtree pull first" >&2; exit 1; }

SETTINGS=".claude/settings.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p .claude

merge_settings() {
	jq -s '
		.[0] as $existing
		| .[1] as $fleet
		| $existing
		| .permissions //= {}
		| .permissions.deny //= []
		| .permissions.deny = (
				(.permissions.deny + ($fleet.permissions.deny // []))
				| unique
			)
	' "$SETTINGS" "$FLEET_DENY"
}

if [[ -f "$SETTINGS" ]]; then
	merge_settings >"$SETTINGS.new"
else
	jq '.' "$FLEET_DENY" >"$SETTINGS.new"
fi
mv "$SETTINGS.new" "$SETTINGS"
bash "$SCRIPT_DIR/format-repo-json.sh" "$SETTINGS" || true
echo "Merged fleet edit deny rules into $SETTINGS"

# Ensure .claude/settings.json can be committed when .claude/ is gitignored.
GI=".gitignore"
if [[ -f "$GI" ]] && ! grep -q 'track claude fleet settings' "$GI"; then
	if grep -qE '^\.claude(/\*\*)?/?$|^\.claude/\*' "$GI"; then
		cat >>"$GI" <<'EOF'

# track claude fleet settings
!.claude/
.claude/*
!.claude/settings.json
EOF
		echo "Appended .claude/settings.json exceptions to $GI"
	fi
fi
