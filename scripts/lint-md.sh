#!/usr/bin/env bash
# Lint markdown with the markdownlint-cli2 version pinned in package.json / package-lock.json.
# Pass --fix to auto-fix violations: bash scripts/lint-md.sh --fix
#
# Prefer the locally installed binary (`npm ci`, run by the installer): it runs offline, so the
# pre-push gate needs no registry egress. Only if the tool isn't installed do we fall back to npx
# — which fetches from the registry and so needs network. Keep the fallback's @0.22.1 pin in sync
# with package.json.
set -euo pipefail
cd "$(dirname "$0")/.."
bin="node_modules/.bin/markdownlint-cli2"
if [[ -x "$bin" ]]; then
  cmd=("$bin")
else
  # Fresh worktrees carry no node_modules. Mirror the pre-push .venv borrow:
  # reuse the MAIN checkout's binary when package-lock.json is byte-identical
  # (offline, zero setup); else fall back to npx. See AGENTS.md for rationale.
  main_root="$(cd "$(dirname "$(git rev-parse --git-common-dir 2>/dev/null)")" 2>/dev/null && pwd || echo "")"
  main_bin="$main_root/node_modules/.bin/markdownlint-cli2"
  if [[ -n "$main_root" && "$main_root" != "$PWD" && -x "$main_bin" ]] \
     && [[ -f package-lock.json && -f "$main_root/package-lock.json" ]] \
     && cmp -s package-lock.json "$main_root/package-lock.json"; then
    echo "lint-md: borrowing main checkout's markdownlint-cli2 ($main_root) — package-lock.json matches." >&2
    cmd=("$main_bin")
  else
    echo "lint-md: $bin not found — run 'npm run worktree:init' (or 'npm ci'). Falling back to npx (fetches from the registry)." >&2
    cmd=(npx --yes markdownlint-cli2@0.22.1)
  fi
fi
exec "${cmd[@]}" "$@" "**/*.md"
