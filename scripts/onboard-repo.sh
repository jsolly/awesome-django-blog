#!/usr/bin/env bash
# First-time (and idempotent re-)onboarding for a repo that already has the .agents/ fleet
# subtree. Ships in the bundle at .agents/scripts/onboard-repo.sh and auto-propagates.
#
# Usage from repo root (after the subtree exists):
#   git remote add dotagents git@github.com:jsolly/dotagents.git
#   git subtree add --prefix=.agents dotagents fleet --squash
#   bash .agents/scripts/onboard-repo.sh
#
# Re-running on an already-onboarded repo upgrades it to the current shims/workflow and
# converges shape (safe and idempotent).
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
[[ -d .agents ]] || { echo "No .agents/ — add the fleet subtree first (see header)" >&2; exit 1; }

REMOTE="${DOTAGENTS_REMOTE:-dotagents}"
BRANCH="${DOTAGENTS_BRANCH:-fleet}"
TPL=".agents/templates"

# 1. Install the thin repo shims + the fleet-lock-guard workflow from the bundle.
mkdir -p scripts .github/workflows
install -m 755 "$TPL/update-agents-subtree.sh" scripts/update-agents-subtree.sh
install -m 755 "$TPL/cloud-fleet-sync-if-stale.sh" scripts/cloud-fleet-sync-if-stale.sh
install -m 644 "$TPL/fleet-lock-guard.yml" .github/workflows/fleet-lock-guard.yml

# 2. AGENTS.md: ensure the @.agents/AGENTS.md import and a ## Cursor Cloud pointer.
python3 - <<'PY'
import pathlib

p = pathlib.Path("AGENTS.md")
text = p.read_text(encoding="utf-8") if p.exists() else ""

# Import line.
if "@.agents/AGENTS.md" not in text:
    text = text.replace("@~/.agents/AGENTS.md", "@.agents/AGENTS.md")
    if "@.agents/AGENTS.md" not in text:
        lines = text.splitlines()
        if lines and lines[0].startswith("# AGENTS.md"):
            lines = [lines[0], "", "@.agents/AGENTS.md", ""] + lines[1:]
        else:
            lines = ["@.agents/AGENTS.md", ""] + lines
        text = "\n".join(lines) + ("\n" if not text.endswith("\n") else "")

# ## Cursor Cloud section (points at the subtree doc).
if "## Cursor Cloud" not in text:
    insert = (
        "## Cursor Cloud\n\n"
        "Cloud agents: see `.agents/docs/cloud-agents.md` (fleet layout, subtree updates, "
        "install-only `environment.json` — no committed snapshot pin).\n\n"
    )
    for heading in ("## Project", "## Purpose", "## Commands", "## Stack"):
        if heading in text:
            text = text.replace(heading, insert + heading, 1)
            break
    else:
        text = text.rstrip() + "\n\n" + insert

p.write_text(text, encoding="utf-8")
PY

# 3. .gitignore: append the cursor snippet once (track cloud config + rules).
python3 - "$TPL/gitignore-cursor-snippet.txt" <<'PY'
import pathlib
import sys

snippet = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
gi = pathlib.Path(".gitignore")
text = gi.read_text(encoding="utf-8") if gi.exists() else ""
if "track cloud config and rules" not in text:
    # Drop any bare `.cursor/` ignore so cloud config can be tracked.
    kept = [ln for ln in text.splitlines() if ln.strip().rstrip("/") != ".cursor"]
    text = "\n".join(kept).rstrip() + "\n\n" + snippet
    gi.write_text(text, encoding="utf-8")
PY

# 4. .cursor/environment.json: strip committed snapshot pin keys (cloud runs install each boot).
if [[ -f .cursor/environment.json ]]; then
  python3 - <<'PY'
import json
import pathlib

p = pathlib.Path(".cursor/environment.json")
data = json.loads(p.read_text(encoding="utf-8"))
changed = False
for key in ("snapshot", "agentCanUpdateSnapshot"):
    if key in data:
        del data[key]
        changed = True
if changed:
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY
fi

# 5. Converge shape (rule links, git guard, workflow ref, stale-file cleanup).
bash .agents/scripts/converge-repo.sh

# 6. Record the fleet HEAD in FLEET.lock when the remote is reachable.
if git rev-parse "${REMOTE}/${BRANCH}^{commit}" &>/dev/null; then
  printf 'sha: %s\n' "$(git rev-parse "${REMOTE}/${BRANCH}^{commit}")" > .agents/FLEET.lock
fi

git add -A
git diff --cached --quiet || git commit -m "chore(agents): onboard fleet subtree (shims, workflow, rules)"

echo "Onboarded $(basename "$ROOT")"
