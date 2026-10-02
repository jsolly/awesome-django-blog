#!/usr/bin/env bash
((BASH_VERSINFO[0] >= 5)) || { echo "✗ $0 requires Bash >= 5, not $BASH_VERSION. Fix: brew install bash; rerun bash ~/code/dotagents/setup/install-local-agent-runtime.sh; open a new shell." >&2; exit 1; }
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source "${DOTAGENTS_GATE_LIB:-$HOME/code/dotagents/gate/gate-lib.sh}"
gate_require_node
npm ci
echo "✓ Node dependencies installed in $PWD"
