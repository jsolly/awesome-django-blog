#!/usr/bin/env bash
# Write a Cursor Cloud snapshot ID into .cursor/environment.json.
# Run from repo root after install succeeds and you have a real snapshot ID.
#
#   ./scripts/pin-cloud-snapshot.sh 'snapshot-20260212-00000000-0000-0000-0000-000000000000'
#   SNAPSHOT_ID='snapshot-...' ./scripts/pin-cloud-snapshot.sh
#
# Do not guess IDs — omit snapshot entirely if you do not have one.

set -euo pipefail

SNAPSHOT="${1:-${SNAPSHOT_ID:-${CURSOR_SNAPSHOT_ID:-}}}"
ENV_FILE=".cursor/environment.json"

if [[ -z "$SNAPSHOT" ]]; then
  echo "Usage: $0 <snapshot-id>" >&2
  echo "Or set SNAPSHOT_ID or CURSOR_SNAPSHOT_ID in the environment." >&2
  exit 1
fi

if [[ ! "$SNAPSHOT" =~ ^snapshot- ]]; then
  echo "WARN: expected snapshot ID to start with 'snapshot-' (got: ${SNAPSHOT:0:40}...)" >&2
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — create environment.json before pinning a snapshot." >&2
  exit 2
fi

export SNAPSHOT
python3 <<'PY'
import json
import os

path = ".cursor/environment.json"
snapshot = os.environ["SNAPSHOT"]

with open(path, encoding="utf-8") as f:
    data = json.load(f)

data["snapshot"] = snapshot
data["agentCanUpdateSnapshot"] = True

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print(f"Updated {path} with snapshot={snapshot}")
PY
