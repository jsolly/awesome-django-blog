# Sync-fleet skill evals

Use this file before changing `SKILL.md` frontmatter.

## Positive load cases

The `sync-fleet` skill should load for:

- `/sync-fleet`
- `Sync all my local repos with the latest fleet`
- `Update .agents/ in every repo under ~/code`
- `Refresh FLEET.lock across my projects`
- `I shipped a new skill to dotagents — sync it into all app repos`
- `Wire local Cursor skills after pulling dotagents`

## Negative neighbor cases

The `sync-fleet` skill should not load for:

- `Sync fleet in this repo only` inside a cloud agent session → use `cloud-fleet-sync-if-stale.sh`
- `/review-fix-push-babysit ship this` → use review-fix-push-babysit (includes fleet gate for one repo)
- `git pull origin main` on dotagents → normal git, not fleet subtree sync
- `Push my fleet sync commits` → git push workflow, not this skill
- `Edit the seo skill in dotagents` → edit upstream in dotagents, then sync

## Forbidden-load cases

- `/seo stocktextalerts.com` → seo skill
- `/review-fix-push-babysit my changes` → review-fix-push-babysit skill
- `Deploy stocktextalerts to Vercel` → deploy workflow, not fleet sync

## Progressive-read expectations

- Read `orchestration.md` for any multi-repo sync run.
- Keep `SKILL.md` concise; script flags and edge cases live in orchestration.

## Routing description target

```yaml
description: Use when the user says `/sync-fleet`, asks to sync the agent fleet, sync all local repos, update `.agents/` subtrees fleet-wide, refresh FLEET.lock across repos, or wire local Cursor skills after dotagents changes. Do NOT use for syncing a single repo inside Cursor Cloud (use `cloud-fleet-sync-if-stale.sh`), pushing commits, editing dotagents canonical files, or routine git pull/push unrelated to the fleet subtree.
```
