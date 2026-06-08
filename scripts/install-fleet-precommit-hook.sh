#!/usr/bin/env bash
# Install or refresh the fleet freshness block in the repo's tracked pre-commit hook.
# Ships in the bundle at .agents/scripts/install-fleet-precommit-hook.sh and auto-propagates.
# Idempotent; does not overwrite non-shell hooks. Standardizes repos on .git-hooks.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

CHECKER=".agents/scripts/fleet-precommit-check.sh"
BEGIN='# BEGIN dotagents fleet pre-commit guard'
END='# END dotagents fleet pre-commit guard'
HOOK=".git-hooks/pre-commit"

find_existing_hook() {
  local hp
  hp="$(git config --local core.hooksPath 2>/dev/null || true)"
  hp="${hp%/}"

  if [[ -n "$hp" && "$hp" != ".git-hooks" && "$hp" != ".husky/_" && -f "$hp/pre-commit" ]]; then
    echo "$hp/pre-commit"
    return
  fi

  for candidate in .husky/pre-commit .githooks/pre-commit .git/hooks/pre-commit; do
    [[ -f "$candidate" ]] || continue
    echo "$candidate"
    return
  done
}

fleet_block() {
  cat <<BLOCK
$BEGIN
ROOT="\$(git rev-parse --show-toplevel)"
if [ -x "\$ROOT/$CHECKER" ]; then
  bash "\$ROOT/$CHECKER" || exit 1
fi
$END
BLOCK
}

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "install-fleet-precommit-hook: not a git repository — skipping" >&2
  exit 0
fi

if [[ ! -f "$CHECKER" ]]; then
  echo "install-fleet-precommit-hook: missing $CHECKER — run fleet sync first" >&2
  exit 0
fi

HOOK_DIR="$(dirname "$HOOK")"
mkdir -p "$HOOK_DIR" .git/hooks

BLOCK_CONTENT="$(fleet_block)"

if [[ ! -f "$HOOK" ]]; then
  existing="$(find_existing_hook || true)"
  if [[ -n "$existing" ]]; then
    cp "$existing" "$HOOK"
  else
    {
      echo '#!/bin/sh'
      echo "$BLOCK_CONTENT"
    } >"$HOOK"
  fi
  chmod +x "$HOOK"
fi

set +e
python3 - "$HOOK" "$BEGIN" "$END" "$BLOCK_CONTENT" "$CHECKER" <<'PY'
import pathlib
import shlex
import sys

hook_path, begin, end, block, checker = sys.argv[1:6]
text = pathlib.Path(hook_path).read_text(encoding="utf-8")
lines = text.splitlines()


def is_shell_shebang(line):
    if not line.startswith("#!"):
        return False

    try:
        parts = shlex.split(line[2:].strip())
    except ValueError:
        parts = line[2:].strip().split()

    if not parts:
        return False

    executable = pathlib.PurePosixPath(parts[0]).name
    if executable == "env":
        for part in parts[1:]:
            if part.startswith("-"):
                continue
            executable = pathlib.PurePosixPath(part).name
            break

    return executable in {"sh", "bash", "dash", "ksh", "zsh"}


first_line = lines[0] if lines else ""
if first_line.startswith("#!") and not is_shell_shebang(first_line):
    print(f"WARN: {hook_path} is not a shell hook — add the fleet guard manually:", file=sys.stderr)
    print(f"  bash {checker} || exit 1", file=sys.stderr)
    sys.exit(2)

if begin in text and end in text:
    before, _, rest = text.partition(begin)
    _, _, after = rest.partition(end)
    text = before + after

shebang = None
body_lines = []
for line in text.splitlines():
    if is_shell_shebang(line):
        if shebang is None:
            shebang = line
        continue
    body_lines.append(line)

if shebang is None:
    shebang = "#!/bin/sh"

while body_lines and body_lines[0] == "":
    body_lines.pop(0)

body = "\n".join(body_lines)
new_text = shebang + "\n" + block.strip() + "\n"
if body:
    new_text += "\n" + body + "\n"
pathlib.Path(hook_path).write_text(new_text, encoding="utf-8")
PY
code=$?
set -e
if [[ "$code" -eq 2 ]]; then
  exit 0
fi
if [[ "$code" -ne 0 ]]; then
  exit "$code"
fi

chmod +x "$HOOK"
git config core.hooksPath .git-hooks
echo "Updated fleet pre-commit guard in $HOOK"
