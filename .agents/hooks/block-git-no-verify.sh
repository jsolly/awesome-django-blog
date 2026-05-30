#!/usr/bin/env bash
# Block git push/commit with --no-verify for Claude, Cursor, and Codex agent hooks.
set -euo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.command // .tool_input.command // ""')

[[ -n "$cmd" ]] || exit 0

block_msg='git push/commit with --no-verify is blocked. Fix the failing hook instead of bypassing it.'

segment_has_no_verify_flag() {
  local segment="$1"
  local stripped
  stripped=$(printf '%s' "$segment" | sed -E "s/'[^']*'//g; s/\"[^\"]*\"//g")
  printf '%s' "$stripped" | grep -qE '(^|[[:space:]])--no-verify([[:space:]]|$)'
}

should_block=false
while IFS= read -r segment || [[ -n "${segment:-}" ]]; do
  segment=$(printf '%s' "$segment" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
  [[ -z "$segment" ]] && continue
  if segment_has_no_verify_flag "$segment" \
    && printf '%s' "$segment" | grep -qE '(^|[[:space:]])(/[^[:space:]]+/git|git)[[:space:]]+(push|commit)([[:space:]]|$)'; then
    should_block=true
    break
  fi
done < <(printf '%s' "$cmd" | tr '&|;' '\n' | sed 's/&&/\n/g' | sed 's/||/\n/g')

$should_block || {
  if printf '%s' "$input" | jq -e '.command' >/dev/null 2>&1; then
    echo '{"permission":"allow"}'
  fi
  exit 0
}

if printf '%s' "$input" | jq -e '.command' >/dev/null 2>&1; then
  jq -n --arg um "$block_msg" --arg am "$block_msg" '{
    permission: "deny",
    user_message: $um,
    agent_message: $am
  }'
  exit 0
fi

jq -n --arg reason "$block_msg" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: $reason
  }
}'
exit 2
