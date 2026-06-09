#!/usr/bin/env bash
# Materialize the dotagents fleet into this repo's gitignored .agents/, then wire .cursor/.
#
# Fleet content is treated like node_modules: NEVER committed, fetched on demand. A repo's
# TRACKED tree stays repo-specific only; this script lays down the shared fleet at runtime.
#
#   - Laptop:  build straight from the local canonical checkout (DOTAGENTS_ROOT or ~/code/dotagents).
#   - Cloud:   clone the published `fleet` branch from GitHub (auth via FLEET_SYNC_TOKEN when set).
#
# This file is canonical in dotagents and is committed (verbatim) into each consuming repo so it
# can run on a fresh Cursor Cloud VM, where ~/ is unavailable. It is the only fleet logic a repo
# commits; everything else under .agents/ is gitignored and produced here.
#
#   bash scripts/bootstrap-repo-fleet.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
DEST="$ROOT/.agents"

DOT="${DOTAGENTS_ROOT:-$HOME/code/dotagents}"
if [[ -d "$DOT/.git" && -x "$DOT/scripts/build-fleet.sh" ]]; then
  # Laptop / any box with the canonical checkout: build the bundle from source.
  echo "bootstrap: building fleet from local checkout at $DOT"
  bash "$DOT/scripts/build-fleet.sh" "$DEST"
else
  # Cloud / no local checkout: fetch the already-built published fleet branch.
  : "${FLEET_REPO:=github.com/jsolly/dotagents.git}"
  if [[ -n "${FLEET_SYNC_TOKEN:-}" ]]; then
    remote="https://${FLEET_SYNC_TOKEN}@${FLEET_REPO}"
  else
    remote="https://${FLEET_REPO}"
  fi
  echo "bootstrap: fetching published fleet branch"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT
  git clone --depth 1 --branch fleet "$remote" "$tmp/fleet" >/dev/null
  rm -rf "$DEST"
  mkdir -p "$DEST"
  git -C "$tmp/fleet" archive HEAD | tar -x -C "$DEST"
fi

# Wire .cursor discovery (skills/agents/rules) + git/edit guards from the materialized fleet.
# These helpers preserve repo-authored real files and only manage fleet symlinks.
[[ -x "$DEST/scripts/link-fleet-cursor.sh" ]] && bash "$DEST/scripts/link-fleet-cursor.sh"
[[ -x "$DEST/scripts/merge-cursor-hooks.sh" ]] && bash "$DEST/scripts/merge-cursor-hooks.sh"
[[ -x "$DEST/scripts/merge-claude-edit-guard.sh" ]] && bash "$DEST/scripts/merge-claude-edit-guard.sh"

echo "bootstrap: materialized fleet into .agents/ (gitignored) and wired .cursor/"
