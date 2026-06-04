#!/usr/bin/env bash
# Install or refresh the fleet freshness block in .git/hooks/pre-commit.
# Ships in the bundle at .agents/scripts/install-fleet-precommit-hook.sh and auto-propagates.
# Idempotent; does not overwrite non-shell hooks.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

HOOK=".git/hooks/pre-commit"
CHECKER=".agents/scripts/fleet-precommit-check.sh"
BEGIN='# BEGIN dotagents fleet pre-commit guard'
END='# END dotagents fleet pre-commit guard'

fleet_block() {
  cat <<BLOCK
$BEGIN
ROOT="\$(git rev-parse --show-toplevel)"
if [[ -x "\$ROOT/$CHECKER" ]]; then
  bash "\$ROOT/$CHECKER" || exit 1
fi
$END
BLOCK
}

if [[ ! -d .git ]]; then
  echo "install-fleet-precommit-hook: not a git repository — skipping" >&2
  exit 0
fi

if [[ ! -f "$CHECKER" ]]; then
  echo "install-fleet-precommit-hook: missing $CHECKER — run fleet sync first" >&2
  exit 0
fi

mkdir -p .git/hooks

if [[ -f "$HOOK" ]] && ! head -n1 "$HOOK" | grep -qE '^#!.*(sh|bash)'; then
  echo "WARN: $HOOK is not a shell hook — add the fleet guard manually:" >&2
  echo "  bash $CHECKER || exit 1" >&2
  exit 0
fi

BLOCK_CONTENT="$(fleet_block)"

if [[ ! -f "$HOOK" ]]; then
  {
    echo '#!/bin/sh'
    echo 'set -e'
    echo "$BLOCK_CONTENT"
  } >"$HOOK"
  chmod +x "$HOOK"
  echo "Installed fleet pre-commit guard at $HOOK"
  exit 0
fi

python3 - "$HOOK" "$BEGIN" "$END" "$BLOCK_CONTENT" <<'PY'
import pathlib
import sys

hook_path, begin, end, block = sys.argv[1:5]
text = pathlib.Path(hook_path).read_text(encoding="utf-8")
if begin in text and end in text:
    before, _, rest = text.partition(begin)
    _, _, after = rest.partition(end)
    new_text = before.rstrip() + "\n\n" + block.strip() + "\n" + after.lstrip("\n")
    if not new_text.endswith("\n"):
        new_text += "\n"
    pathlib.Path(hook_path).write_text(new_text, encoding="utf-8")
else:
    new_text = text.rstrip() + "\n\n" + block.strip() + "\n"
    if not new_text.endswith("\n"):
        new_text += "\n"
    pathlib.Path(hook_path).write_text(new_text, encoding="utf-8")
PY

chmod +x "$HOOK"
echo "Updated fleet pre-commit guard in $HOOK"
