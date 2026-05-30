# Cursor Cloud Agents

This repo is configured for **cloud-only development**: agents, skills, and rules are self-contained in git (no `.agents/` on the VM).

## Layout

```text
<repo>/
├── AGENTS.md                         # @.agents/AGENTS.md + ## Project / ## Purpose
├── .agents/                          # git subtree from dotagents (fleet branch)
│   ├── AGENTS.md                     # fleet persona + collaboration
│   ├── agents/                       # review-fix-push subagent prompts
│   ├── skills/                       # review-fix, review-fix-push
│   ├── rules/                        # canonical guidelines (.md, Cursor frontmatter)
│   └── scripts/
│       └── link-fleet-rules.sh       # wire .agents/rules into .cursor/rules/ (fleet-vendored)
├── .cursor/
│   ├── environment.json              # cloud VM install (+ optional terminals)
│   └── rules/                        # fleet symlinks (.mdc) + project-only rules
└── scripts/
    ├── update-agents-subtree.sh      # pull fleet updates from dotagents
    └── pin-cloud-snapshot.sh         # commit snapshot ID after first green cloud boot
```

Cloud agents discover:

- **Skills** at `.agents/skills/`
- **Rules** at `.cursor/rules/` (fleet + project)
- **Instructions** from root `AGENTS.md`

They do **not** see `.agents/`, `~/.cursor/skills/`, or local symlinks outside the repo.

## Environment

See `.cursor/environment.json`. New repos ship with `"agentCanUpdateSnapshot": true` so Cursor may let the agent refresh the pinned snapshot when the platform supports it (see [environment schema](https://www.cursor.com/schemas/environment.schema.json)).

**Project-local paths (never overwritten by fleet subtree pull):** `.agents/hooks/`, `.agents/automations/` — commit these in the child repo only; they are not in the dotagents `fleet` branch.

## Snapshot bootstrap (agent-run)

Run this **once per repo** (or again after dependency/toolchain changes) when you are a **Cursor Cloud agent** and `.cursor/environment.json` has no `snapshot` field, has a stale snapshot, or the user asked you to refresh the cloud environment.

1. **Verify install** — Re-run or confirm the `install` command from `.cursor/environment.json` succeeded. Then run a **smoke check** from root `AGENTS.md` (e.g. `npm run check:ts`, `npm test`, project-specific command). Do not pin a snapshot on a broken environment.

2. **Obtain a snapshot ID** (real ID only; never guess):
   - Check agent UI / session metadata for a snapshot or environment ID after setup completes.
   - Check env vars: `CURSOR_SNAPSHOT_ID`, `SNAPSHOT_ID` (if Cursor injected one).
   - If still missing: open [Cloud Agents → Environments](https://cursor.com/dashboard?tab=cloud-agents), find this repository’s saved environment, and use **Copy** on the Snapshot column (requires an authenticated browser session — use browser tools if available, otherwise ask the user to paste the ID).

3. **Pin in the repo:**

   ```bash
   ./scripts/pin-cloud-snapshot.sh 'snapshot-YYYYMMDD-...'
   ```

4. **Commit and push** on the working branch:

   ```bash
   git add .cursor/environment.json
   git commit -m "chore(agents): pin cloud environment snapshot"
   git push
   ```

5. **Subtree sync** — If you also changed fleet docs under `.agents/`, run `./scripts/update-agents-subtree.sh` only when pulling from dotagents, not after pinning a snapshot.

If you cannot obtain a snapshot ID, **leave `snapshot` unset** and note the blocker in your summary. The next agent will boot from `install` only.

## Fleet updates (dotagents subtree)

Fleet config is vendored from [dotagents](https://github.com/jsolly/dotagents) `fleet` branch via [git subtree](https://gist.github.com/SKempin/b7857a6ff6bddb05717cc17a44091202).

**Pull latest fleet into this repo:**

```bash
./scripts/update-agents-subtree.sh
```

**Edit fleet canonical copy** (on a machine with a `~/.agents` checkout):

```bash
cd ~/.agents
# edit agents/, skills/, rules/
git add -A && git commit -m "..." && git push   # CI rebuilds + publishes the fleet branch
```

Then in this repo: `./scripts/update-agents-subtree.sh` (or wait for the weekly sync).

**Note:** `.agents/` in this repo is **read-only** — pull-only. The `fleet` branch is published by dotagents CI from `.agents/`; editing `.agents/` here and pushing back upstream does not round-trip (the next CI publish overwrites it). Make fleet changes in `.agents/`.

### GitHub Actions weekly sync

Repos with `.github/workflows/sync-agent-fleet.yml` pull fleet automatically (Monday 6am UTC) or via **Actions → Sync agent fleet → Run workflow**.

Because `dotagents` is private, each repo needs a **repository secret**:

| Secret | Value |
| --- | --- |
| `FLEET_SYNC_TOKEN` | Fine-grained PAT: **read-only** access to `jsolly/dotagents` (Contents) |

Do **not** reuse `GH_AGENT_TOKEN` (Cursor cloud agents) — that token has broader cross-repo scope and should stay in Cursor secrets only. The workflow push back to the same repo uses the built-in `GITHUB_TOKEN`.

## Project-only vs fleet

| Asset | Location | Synced from dotagents? |
| --- | --- | --- |
| Fleet persona, review skills, code-style rules | `.agents/` | Yes (subtree) |
| Project-only Cursor rules | `.cursor/rules/*.mdc` (real files) | No |
| Dev environment | `.cursor/environment.json` | No (per-repo) |
| Commands, architecture | `AGENTS.md` sections below `@.agents/` | No |

## References

- [Cursor Cloud Agent setup](https://cursor.com/docs/cloud-agent/setup)
- [Cursor Skills](https://cursor.com/docs/skills)
