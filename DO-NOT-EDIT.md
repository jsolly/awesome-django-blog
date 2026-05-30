# DO NOT EDIT — fleet-managed subtree

This directory is a **read-only git subtree** from [dotagents](https://github.com/jsolly/dotagents) (`fleet` branch). The next fleet sync **overwrites every file here**.

## Do not modify in this repo

- **`.agents/**`** — entire subtree (skills, rules, agents, hooks, scripts, docs, templates)
- **`scripts/update-agents-subtree.sh`** — reinstalled from `.agents/templates/`
- **`scripts/cloud-fleet-sync-if-stale.sh`** — reinstalled from `.agents/templates/`
- **`.github/workflows/fleet-lock-guard.yml`** — reinstalled from `.agents/templates/`

## Where to make changes

Edit the canonical source in **`~/code/dotagents`** (or your dotagents clone), commit to `main`, and let CI publish the `fleet` branch. Child repos pull via `scripts/update-agents-subtree.sh` or `scripts/cloud-fleet-sync-if-stale.sh`.

## Project-owned surfaces (safe to edit)

- Root `AGENTS.md` sections below `@.agents/AGENTS.md`
- `.cursor/rules/*.mdc` — real files (not fleet symlinks)
- `.cursor/environment.json`, project hooks beyond fleet merges
- Application source code outside the paths above

See `.agents/docs/cloud-agents.md` for layout and sync workflow.
