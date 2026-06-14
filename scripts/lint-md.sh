#!/usr/bin/env bash
# Lint markdown with the markdownlint-cli2 version pinned in package.json / package-lock.json.
# Pass --fix to auto-fix violations: bash scripts/lint-md.sh --fix
#
# Prefer the locally installed binary (`npm ci`, run by the installer): it runs offline, so the
# pre-push gate works inside Claude Code's command sandbox with no registry egress. Only if the
# tool isn't installed do we fall back to npx — which fetches from the registry and so needs
# network (and the sandbox disabled). Keep the fallback's @0.22.1 pin in sync with package.json.
set -euo pipefail
cd "$(dirname "$0")/.."
bin="node_modules/.bin/markdownlint-cli2"
if [[ -x "$bin" ]]; then
  cmd=("$bin")
else
  echo "lint-md: $bin not found — run 'npm ci'. Falling back to npx (fetches from the registry)." >&2
  cmd=(npx --yes markdownlint-cli2@0.22.1)
fi
exec "${cmd[@]}" "$@" "**/*.md"
