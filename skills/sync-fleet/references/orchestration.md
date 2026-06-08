# Sync-fleet orchestration

## Phase 0: Scope

Confirm:

- Scan root — default `FLEET_SCAN_ROOT=~/code`. Override when the user keeps repos elsewhere.
- Single repo — pass `--repo <name>` (basename under the scan root) to sync one checkout.
- Local runtime — pass `--with-local-runtime` to re-run `install-local-agent-runtime.sh` after sync when dotagents skills changed.
- Dry run — use `--dry-run` when many repos may be dirty; show what would run without mutating.

This skill does **not** push commits. Tell the user which repos gained local `chore(fleet)` commits if they care about origin.

## Phase 1: Preflight

1. Ensure `dotagents` remote is reachable (`git fetch dotagents fleet` from any repo, or rely on per-repo fetch inside the script).
2. Optionally `git -C ~/code/dotagents pull --ff-only` so local skill symlinks target current `main` (separate from fleet subtree).
3. Run the helper:

```bash
bash skills/sync-fleet/scripts/sync-local-fleet-repos.sh [--dry-run] [--with-local-runtime]
```

Or from dotagents root:

```bash
bash skills/sync-fleet/scripts/sync-local-fleet-repos.sh
```

## Phase 2: Interpret results

The script prints JSON to stdout:

- `targetFleetSha` — HEAD of `dotagents/fleet` used for comparison
- `repos[]` — per repo: `name`, `status`, `fleetSha`, `skills`, `aheadOfOrigin`, `note`

Status values:

| Status | Meaning |
| --- | --- |
| `synced` | Subtree pull and/or converge committed |
| `already_current` | Lock matched fleet; converge only (or no-op) |
| `skipped_dirty` | Uncommitted changes — user must commit/stash first |
| `skipped_no_shim` | Missing `scripts/update-agents-subtree.sh` |
| `failed` | Updater exited non-zero — see stderr in agent logs |
| `dry_run` | Would sync (with `--dry-run`) |

Present a short table to the user. Call out dirty repos explicitly.

## Phase 3: Local runtime (optional)

When `--with-local-runtime` or the user asked to refresh Cursor discovery:

```bash
bash ~/code/dotagents/scripts/install-local-agent-runtime.sh personal
```

Use `work` only when the user confirms a work laptop profile.

## Gotchas

- **cwd matters.** Each updater must run with `cd <repo-root>` first. Running from the wrong directory syncs the wrong repo (or the same repo repeatedly).
- **Dirty trees block subtree pull.** Skipping is intentional — do not stash without explicit user approval.
- **Converge-only commits can fail hooks** when hook JSON changes are whitespace-only (e.g. Biome/lint-staged "empty commit"). Fleet content may still be updated; report hook drift separately.
- **Unpushed commits accumulate.** Each synced repo may be several commits ahead of origin; that is normal.
- **Cloud agents** have one repo — use `./scripts/cloud-fleet-sync-if-stale.sh` instead of this skill.
