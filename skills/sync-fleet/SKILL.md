---
name: sync-fleet
description: Use when the user says `/sync-fleet`, asks to sync the agent fleet, sync all local repos, update `.agents/` subtrees fleet-wide, refresh FLEET.lock across repos, or wire local Cursor skills after dotagents changes. Do NOT use for syncing a single repo inside Cursor Cloud (use `cloud-fleet-sync-if-stale.sh`), pushing commits, editing dotagents canonical files, or routine git pull/push unrelated to the fleet subtree.
effort: medium
---

# Sync agent fleet across local repos

Desktop-only meta skill. Pulls the latest `dotagents/fleet` bundle into every clean app repo under a scan root (default `~/code`), runs converge, and reports a summary.

## Required first reads

1. Read `references/evals.md` if you are changing this skill.
2. Read `references/orchestration.md` before any full `/sync-fleet` run.

## Operating principle

Sync is **local-only** and **never pushes**. Each repo must have a clean working tree. Always `cd` into the repo root before running its `scripts/update-agents-subtree.sh` shim — never run the updater from another checkout's cwd.

## Workflow summary

1. Confirm scan root (default `~/code`) and whether to refresh local Cursor symlinks (`--with-local-runtime`).
2. Run `scripts/sync-local-fleet-repos.sh` (add `--dry-run` first when the user has many dirty repos).
3. Report synced / skipped / failed repos with fleet SHA and whether `/seo` (or other new skills) landed.
4. Remind the user that local fleet commits are unpushed until they choose to ship each repo.

Full details: `references/orchestration.md`.

## Helper script

From this skill directory:

```bash
scripts/sync-local-fleet-repos.sh [--dry-run] [--with-local-runtime] [--scan-root ~/code] [--repo stocktextalerts]
```

Stdout: JSON summary. Stderr: per-repo progress.

## Safety rules

- Never push, never `--no-verify`, never `git add -A` in app repos.
- Skip dirty repos; list them for the user instead of stashing automatically.
- Do not sync repos missing `scripts/update-agents-subtree.sh`.
- Do not claim success for a repo whose `FLEET.lock` still differs from `dotagents/fleet` HEAD.

## Maintenance

Append gotchas and eval cases. Change frontmatter only when `references/evals.md` shows a routing failure.
