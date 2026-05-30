#!/usr/bin/env bash
# Symlink fleet rules from .agents/rules/ into .cursor/rules/ as .mdc (Cursor discovery path).
# Project-only rules (real files) are left untouched.
# Stale fleet symlinks (e.g. removed rules) are deleted.
# Run from repo root after subtree add/pull.

set -euo pipefail

FLEET_RULES=".agents/rules"
DEST=".cursor/rules"

if [[ ! -d "$FLEET_RULES" ]]; then
  echo "Missing $FLEET_RULES — run scripts/update-agents-subtree.sh first" >&2
  exit 2
fi

mkdir -p "$DEST"
dest_dir="$(cd "$DEST" && pwd)"

for f in "$FLEET_RULES"/*.md; do
  [[ -f "$f" ]] || continue
  base="$(basename "$f" .md)"
  target="${dest_dir}/${base}.mdc"
  if [[ -e "$target" && ! -L "$target" ]]; then
    echo "Keeping project rule (real file): $target"
    continue
  fi
  link_target="$(python3 -c "import os.path; print(os.path.relpath('${f}', '${dest_dir}'))")"
  ln -sf "$link_target" "$target"
  echo "Linked ${DEST}/${base}.mdc -> $link_target"
done

for target in "$DEST"/*.mdc; do
  [[ -e "$target" ]] || continue
  [[ -L "$target" ]] || continue
  base="$(basename "$target" .mdc)"
  if [[ ! -f "$FLEET_RULES/${base}.md" ]]; then
    rm -f "$target"
    echo "Removed stale fleet symlink: ${DEST}/${base}.mdc"
  fi
done

echo "Done. Fleet rules linked; project-only .mdc files unchanged."
