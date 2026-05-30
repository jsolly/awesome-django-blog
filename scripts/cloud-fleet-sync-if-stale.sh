#!/usr/bin/env bash
# Thin shim (installed once per repo by .agents/scripts/onboard-repo.sh). The real logic
# ships in .agents/scripts/cloud-fleet-sync-if-stale.sh and auto-propagates via the fleet
# subtree. Run it from a temp copy so a triggered subtree pull cannot overwrite the
# executing script mid-run.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
REAL="$ROOT/.agents/scripts/cloud-fleet-sync-if-stale.sh"
if [[ ! -f "$REAL" ]]; then
  echo "Missing $REAL — run ./scripts/update-agents-subtree.sh first" >&2
  exit 1
fi

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
cp "$REAL" "$TMP"
bash "$TMP" "$@"
