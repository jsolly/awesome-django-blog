#!/usr/bin/env bash
# Thin shim (installed once per repo by .agents/scripts/onboard-repo.sh). The real logic
# ships in .agents/scripts/update-agents-subtree.sh and auto-propagates via the fleet
# subtree. Run it from a temp copy so the subtree pull cannot overwrite the executing
# script mid-run.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
REAL="$ROOT/.agents/scripts/update-agents-subtree.sh"
if [[ ! -f "$REAL" ]]; then
  echo "Missing $REAL — add the fleet subtree, then run: bash .agents/scripts/onboard-repo.sh" >&2
  exit 1
fi

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
cp "$REAL" "$TMP"
bash "$TMP" "$@"
