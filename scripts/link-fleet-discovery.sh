#!/usr/bin/env bash
# Symlink fleet skills and review agents into Cursor discovery paths.
# Project-owned real files are left untouched.
set -euo pipefail

link_dir_entries() {
  local source_dir="$1"
  local dest_dir="$2"
  local glob="$3"

  if [[ ! -d "$source_dir" ]]; then
    echo "Missing $source_dir — run scripts/update-agents-subtree.sh first" >&2
    exit 2
  fi

  mkdir -p "$dest_dir"
  local dest_abs
  dest_abs="$(cd "$dest_dir" && pwd)"

  local source path base target link_target
  for source in $glob; do
    [[ -e "$source" ]] || continue
    base="$(basename "$source")"
    target="$dest_abs/$base"
    if [[ -e "$target" && ! -L "$target" ]]; then
      echo "Keeping project-owned discovery file: $target"
      continue
    fi
    path="../../$source_dir/$base"
    ln -sfn "$path" "$target"
    echo "Linked $target -> $path"
  done

  for target in "$dest_dir"/*; do
    [[ -L "$target" ]] || continue
    link_target="$(readlink "$target")"
    case "$link_target" in
      ../../"$source_dir"/*)
        if [[ ! -e "$dest_dir/$link_target" ]]; then
          rm -f "$target"
          echo "Removed stale fleet discovery symlink: $target"
        fi
        ;;
    esac
  done
}

link_dir_entries ".agents/skills" ".cursor/skills" ".agents/skills/*"
link_dir_entries ".agents/agents" ".cursor/agents" ".agents/agents/*.md"

echo "Done. Fleet skills and reviewer agents linked for Cursor discovery."
