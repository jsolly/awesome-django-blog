#!/usr/bin/env bash
# Agent config bootstrap — the single entry each repo vendors (via a minimal subtree of dotagents).
#
# Context-aware:
#   - Dev machine (a dotagents checkout is resolvable) → wire the developer's GLOBAL ~/ by
#     delegating to install-local-agent-runtime.sh. No logic duplicated.
#   - Cursor Cloud VM / headless (no ~/ to read) → fetch the canonical dotagents content and wire
#     the repo-local .cursor/ so cloud agents discover skills/agents/rules + the global guards.
#
# Canonical source of truth is the dotagents repo's content dirs (skills/ agents/ rules/ hooks/);
# there is no separate "bundle build". The materialized copy under .agents/ is gitignored.
set -euo pipefail

DOT="${DOTAGENTS_ROOT:-$HOME/code/dotagents}"
if [[ -d "$DOT/.git" && -x "$DOT/scripts/install-local-agent-runtime.sh" ]]; then
  exec bash "$DOT/scripts/install-local-agent-runtime.sh"
fi

# --- Cloud / headless: fetch canonical content, wire repo-local .cursor/ --------------------
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
DEST="$ROOT/.agents" # gitignored; materialized canonical content

# Guarantee the materialized fleet is never committed by the consuming repo.
gi="$ROOT/.gitignore"
touch "$gi"
grep -qxF '/.agents/' "$gi" || printf '\n# Materialized agent config (fetched by bootstrap.sh; not committed)\n/.agents/\n' >>"$gi"

: "${FLEET_REPO:=github.com/jsolly/dotagents.git}"
if [[ -n "${FLEET_SYNC_TOKEN:-}" ]]; then
  remote="https://${FLEET_SYNC_TOKEN}@${FLEET_REPO}"
else
  remote="https://${FLEET_REPO}"
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git clone --depth 1 "$remote" "$tmp/dotagents" >/dev/null 2>&1 \
  || { echo "bootstrap: failed to fetch canonical agent config from $FLEET_REPO" >&2; exit 1; }

rm -rf "$DEST"
mkdir -p "$DEST"
for d in skills agents rules hooks; do
  [[ -d "$tmp/dotagents/$d" ]] && cp -R "$tmp/dotagents/$d" "$DEST/$d"
done
[[ -f "$tmp/dotagents/AGENTS.md" ]] && cp "$tmp/dotagents/AGENTS.md" "$DEST/AGENTS.md"

# Link discovery into repo-local .cursor/ (skills/agents/rules); keep project-owned real files.
link_into() { # <src_dir> <glob> <dest_dir> <strip_ext> <dest_ext>
  local src_dir="$1" glob="$2" dest_dir="$3" strip="$4" ext="$5"
  [[ -d "$src_dir" ]] || return 0
  mkdir -p "$dest_dir"
  local dest_abs s base name target
  dest_abs="$(cd "$dest_dir" && pwd)"
  for s in $glob; do # word-split is intentional (glob expansion)
    [[ -e "$s" ]] || continue
    base="$(basename "$s")"
    name="${base%"$strip"}"
    target="$dest_abs/${name}${ext}"
    [[ -e "$target" && ! -L "$target" ]] && continue # project-owned real file → keep
    ln -sfn "$s" "$target" # absolute symlink into the materialized .agents/ (no python3 dep)
  done
}
# shellcheck disable=SC2086
link_into "$DEST/rules"  "$DEST/rules/*.md"  "$ROOT/.cursor/rules"  ".md" ".mdc"
# shellcheck disable=SC2086
link_into "$DEST/skills" "$DEST/skills/*"    "$ROOT/.cursor/skills" ""    ""
# shellcheck disable=SC2086
link_into "$DEST/agents" "$DEST/agents/*.md" "$ROOT/.cursor/agents" ""    ""

# Wire the global guards into repo-local .cursor/hooks.json (cloud can't read ~/'s copy).
ch="$ROOT/.cursor/hooks.json"
[[ -f "$ch" ]] || printf '{"version":1,"hooks":{}}\n' >"$ch"
for g in block-git-no-verify block-prod-db-migrations block-stack-delete; do
  jq --arg cmd "bash .agents/hooks/$g.sh" --arg n "$g" '
    .version //= 1
    | .hooks.beforeShellExecution //= []
    | .hooks.beforeShellExecution = [.hooks.beforeShellExecution[]? | select((.command // "") | test($n) | not)]
    | .hooks.beforeShellExecution += [{command: $cmd, failClosed: true, timeout: 10}]
  ' "$ch" >"$ch.new" && mv "$ch.new" "$ch"
done

echo "bootstrap: wired repo-local .cursor/ from canonical agent config (cloud mode)"
