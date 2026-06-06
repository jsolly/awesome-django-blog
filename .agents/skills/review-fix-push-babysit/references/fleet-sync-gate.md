# Fleet Freshness Gate

Run this gate **after step 1 (inspect changes)** and **before step 2 (sync `origin/main`)**. It ensures `.agents/FLEET.lock` matches `dotagents/fleet` before the skill makes any WIP commit, merge, review, or push. Without it, the fleet pre-commit guard blocks the WIP commit in step 2 with an opaque stale-lock error.

Hooks remain **fail-only** — this gate is the supported shipping-path sync. Do not add pre-push auto-sync or use `--no-verify` to bypass stale fleet.

---

## When to skip

Skip the entire gate when **any** of these is true:

- `.agents/FLEET.lock` does not exist (dotagents itself, or a repo without the fleet subtree).
- You are not in an app repo that consumes the fleet subtree.

---

## Prerequisites (fleet consumer repos)

When `.agents/FLEET.lock` exists:

- `./scripts/cloud-fleet-sync-if-stale.sh` must exist and be executable.
- `.agents/scripts/fleet-precommit-check.sh` must exist (bundled in the subtree).
- Network access to fetch `dotagents/fleet` (SSH `dotagents` remote or `DOTAGENTS_GITHUB_TOKEN` / `DOTAGENTS_URL`).

If the sync shim is missing, stop and tell the user to run `./scripts/update-agents-subtree.sh` once to onboard the repo.

---

## Check freshness

From repo root:

```bash
bash .agents/scripts/fleet-precommit-check.sh
```

Interpret exit code:

| Exit | Meaning | Action |
| --- | --- | --- |
| `0` | Lock matches fleet (or no lock — should not happen if you reached prerequisites) | Gate complete — continue to step 2 |
| `1` with "stale" | Lock behind `dotagents/fleet` | Run sync procedure below |
| `1` with fetch/auth error | Cannot reach fleet | Stop — report network/token/remote issue; do not commit or push |

Alternative one-shot check (also runs sync when stale):

```bash
./scripts/cloud-fleet-sync-if-stale.sh
```

Use this for the actual sync step when stale. The pre-commit checker above is read-only and distinguishes current vs stale vs fetch failure without modifying the tree.

---

## Sync when stale

`update-agents-subtree.sh` (invoked by `cloud-fleet-sync-if-stale.sh`) **requires a clean working tree**. The skill often starts dirty, so stash first when needed.

### Clean tree

```bash
./scripts/cloud-fleet-sync-if-stale.sh
```

Expect either:

- `Fleet already at dotagents/fleet (...)` — no-op, continue.
- A new commit: `chore(fleet): sync agent fleet from dotagents` or `chore(fleet): converge agent fleet shape` — **keep this commit** on the branch being shipped.

### Dirty tree

```bash
STASH_MSG="review-fix-push-babysit: fleet sync gate $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git stash push -u -m "$STASH_MSG"
./scripts/cloud-fleet-sync-if-stale.sh
git stash pop --index
```

**Stop conditions after `git stash pop --index`:**

- Merge conflicts in any file — stop. Report conflict paths and the stash name (`git stash list`). Do not commit or push until the user resolves conflicts.
- `stash pop` fails for any other reason — stop with `git status` and stash list output.

If sync itself fails (subtree conflict beyond `FLEET.lock`, network, dirty tree despite stash), stop with the script stderr and `git status`. Do not push.

---

## After the gate

1. Run `git status` and `git diff` again — note any fleet sync commit now on HEAD.
2. Continue to **step 2** (sync `origin/main` into the working branch).
3. The fleet sync commit ships with the rest of the work unless the user explicitly asked to exclude it (rare — it is intentional housekeeping).

---

## What this gate does not do

- **No pre-push hook** — pushing commits made before fleet moved is still possible outside this skill; the gate targets the supported `/review-fix-push-babysit` path only.
- **No hook auto-sync** — pre-commit still only blocks; it never pulls the subtree.
- **No `--no-verify`** — never bypass fleet freshness or other hooks.
