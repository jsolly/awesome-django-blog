#!/usr/bin/env bash
# Symlink fleet rules, skills, and reviewer agents from .agents/ into Cursor discovery paths.
# Replaces link-fleet-rules.sh + link-fleet-discovery.sh. Ships in the bundle at
# .agents/scripts/link-fleet-cursor.sh and auto-propagates. Run from repo root after subtree pull.
#
#   rules:  .agents/rules/*.md  -> .cursor/rules/<name>.mdc
#   skills: .agents/skills/*    -> .cursor/skills/<name>
#   agents: .agents/agents/*.md -> .cursor/agents/<name>.md
#
# Project-owned real files are left untouched; stale fleet symlinks (removed upstream) are pruned.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

relpath() {
  python3 -c "import os.path, sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$1" "$2"
}

# link_fleet_into <src_dir> <src_glob> <dest_dir> <strip_ext> <dest_ext>
# dest filename = <source basename, with strip_ext removed> + dest_ext.
link_fleet_into() {
  local src_dir="$1" src_glob="$2" dest_dir="$3" strip_ext="$4" dest_ext="$5"

  if [[ ! -d "$src_dir" ]]; then
    echo "Skipping $src_dir (not present)" >&2
    return 0
  fi

  mkdir -p "$dest_dir"
  local dest_abs
  dest_abs="$(cd "$dest_dir" && pwd)"

  local src base name target link_target
  for src in $src_glob; do
    [[ -e "$src" ]] || continue
    base="$(basename "$src")"
    name="${base%"$strip_ext"}"
    target="$dest_abs/${name}${dest_ext}"
    if [[ -e "$target" && ! -L "$target" ]]; then
      echo "Keeping project-owned file: $target"
      continue
    fi
    link_target="$(relpath "$src" "$dest_abs")"
    ln -sfn "$link_target" "$target"
    echo "Linked $target -> $link_target"
  done

  # Prune stale fleet symlinks: point into ../../<src_dir>/ but no longer resolve.
  local entry
  for entry in "$dest_dir"/*; do
    [[ -L "$entry" ]] || continue
    link_target="$(readlink "$entry")"
    case "$link_target" in
      ../../"$src_dir"/*)
        if [[ ! -e "$dest_abs/$link_target" ]]; then
          rm -f "$entry"
          echo "Removed stale fleet symlink: $entry"
        fi
        ;;
    esac
  done
}

link_fleet_into ".agents/rules"  ".agents/rules/*.md"  ".cursor/rules"  ".md" ".mdc"
link_fleet_into ".agents/skills" ".agents/skills/*"    ".cursor/skills" ""    ""
link_fleet_into ".agents/agents" ".agents/agents/*.md" ".cursor/agents" ""    ""

echo "Done. Fleet rules, skills, and reviewer agents linked for Cursor discovery."
