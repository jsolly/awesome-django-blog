# Cursor Cloud Agents

<!-- fleet-doc-version: 11 -->

This repo is configured for **cloud agents and local desktop agents** through the same committed app-repo runtime. Skills, reviewer prompts, rules, instructions, and fleet guards are self-contained in git. **Cursor Cloud VMs** have no developer-home checkout — only the committed repo content applies. **Local desktop** Cursor / Claude / Codex use the same subtree when opened inside an app repo, plus the optional local laptop runtime from [dotagents](https://github.com/jsolly/dotagents) (`docs/setup-local-machine.md` in the canonical repo).

## Layout

```text
<repo>/
├── AGENTS.md                         # @.agents/AGENTS.md + ## Project / ## Purpose
├── .agents/                          # git subtree from dotagents (fleet branch) — DO NOT EDIT
│   ├── AGENTS.md                     # fleet persona + collaboration
│   ├── DO-NOT-EDIT.md                # banner: fleet-managed paths (read-only in app repos)
│   ├── agents/                       # review-fix-push-babysit subagent prompts
│   ├── skills/                       # review-fix, review-fix-push-babysit, seo
│   ├── hooks/
│   │   ├── block-git-no-verify.sh    # blocks git push/commit --no-verify (Cursor hook)
│   │   └── block-fleet-edits.sh      # blocks Write/Delete on fleet-managed paths (Cursor hook)
│   ├── rules/                        # canonical guidelines (.md, Cursor frontmatter)
│   ├── FLEET.lock                    # pinned dotagents fleet branch SHA (written on sync in app repos)
│   ├── docs/cloud-agents.md          # this doc (read from the subtree)
│   ├── templates/                    # repo shims, claude-settings.json, workflow installed by onboard-repo.sh
│   └── scripts/                      # self-installing fleet logic (auto-propagates)
│       ├── onboard-repo.sh           # first-time / re-onboard: install shims, converge, lock
│       ├── converge-repo.sh          # idempotent shape convergence (rules, guards, workflow, cleanup)
│       ├── update-agents-subtree.sh  # real subtree updater (run via the scripts/ shim)
│       ├── cloud-fleet-sync-if-stale.sh
│       ├── cloud-install-lib.sh      # shared cloud install helpers (Node, SAM, Playwright E2E, …)
│       ├── fleet-lock-check.sh       # CI lock + content-drift check (fleet-lock-guard.yml)
│       ├── link-fleet-rules.sh       # wire .agents/rules into .cursor/rules/
│       ├── link-fleet-discovery.sh   # wire .agents/skills and .agents/agents into .cursor/
│       ├── merge-cursor-git-guard.sh # merge git guard into .cursor/hooks.json
│       ├── merge-cursor-edit-guard.sh # merge fleet edit guard into .cursor/hooks.json
│       └── merge-claude-edit-guard.sh # merge Edit/Write deny rules into .claude/settings.json
├── .claude/
│   └── settings.json                 # fleet Edit/Write deny rules (merged by converge-repo.sh)
├── .github/workflows/
│   └── fleet-lock-guard.yml          # verifies FLEET.lock + .agents/ content on PRs touching .agents/
├── .cursor/
│   ├── environment.json              # cloud VM install (+ optional terminals)
│   ├── hooks.json                    # git guard + fleet edit guard (+ project hooks)
│   └── rules/                        # fleet symlinks (.mdc) + project-only rules
└── scripts/                          # thin shims (copy fleet logic to a tmp file, run it)
    ├── update-agents-subtree.sh
    └── cloud-fleet-sync-if-stale.sh
```

Cloud agents discover:

- **Skills** at `.cursor/skills/` symlinked to `.agents/skills/`
- **Reviewer agent prompts** at `.cursor/agents/` symlinked to `.agents/agents/`
- **Fleet persona** at `.agents/AGENTS.md` (included via root `AGENTS.md`)
- **Rules** at `.cursor/rules/` (fleet symlinks + project-only files)
- **Instructions** from root `AGENTS.md`

They **do** read the committed `.agents/` subtree and repo-local `.cursor/` discovery links. They do **not** see developer-home skill paths, `~/.agents`, user-level `~/.cursor/skills/`, user-level `~/.cursor/agents/`, or machine-local symlinks outside the repo.

### Edit path (fleet changes)

Fleet changes go to [dotagents](https://github.com/jsolly/dotagents) `main` → CI publishes the `fleet` branch → each app repo syncs via **Fleet sync at cloud task start** (below) or `./scripts/update-agents-subtree.sh`. **Never edit `.agents/` in app repos** — the next fleet publish or subtree pull overwrites direct edits.

## Fleet sync at cloud task start (agent-run)

Cloud agents only see **committed** `.agents/` on the branch Cursor cloned. **At the start of each cloud task**, refresh fleet when `FLEET.lock` is behind `dotagents/fleet`.

1. **Secrets** — [Cloud Agents → Secrets](https://cursor.com/dashboard?tab=cloud-agents) for this repository:

   | Secret | Value |
   | --- | --- |
   | `FLEET_SYNC_TOKEN` | Fine-grained PAT: **read-only** Contents on `jsolly/dotagents` (used by `update-agents-subtree.sh` to fetch `fleet`) |

   App-repo push uses Cursor’s normal GitHub access for this repository. Do **not** put `GH_AGENT_TOKEN` in repo secrets for fleet fetch — keep that in Cursor-only config.

2. **Working tree** — `update-agents-subtree.sh` requires a clean tree. Commit or stash unrelated work first.

3. **Check and pull** (from repo root):

   ```bash
   bash scripts/cloud-fleet-sync-if-stale.sh
   ```

   Compares `.agents/FLEET.lock` to `dotagents/fleet`; when stale, runs `./scripts/update-agents-subtree.sh`, which pulls the subtree, writes `FLEET.lock`, runs `converge-repo.sh` (skill/agent/rule links, git/edit guards, Claude deny merge, workflow ref, stale-file cleanup), and **commits the sync automatically**.

4. **Push** the sync commit before feature work:

   ```bash
   git status        # should show a "chore(fleet): sync agent fleet from dotagents" commit ahead
   git push
   ```

   If `git status` shows nothing ahead, the fleet was already current — nothing to push.

If `dotagents` remote is missing, `update-agents-subtree.sh` adds it.

## Environment

See `.cursor/environment.json`. Fleet repos use an `install` command (typically `bash scripts/cloud-agent-install.sh`) and **do not** commit a `"snapshot"` field — every agent boot runs install, then Cursor may reuse internal checkpoints (best-effort; see [Cloud Agent setup](https://cursor.com/docs/cloud-agent/setup)).

After install succeeds, run smoke checks from root `AGENTS.md` (e.g. `npm run check:ts`, `npm test`). Do **not** add `snapshot` or `agentCanUpdateSnapshot` to `environment.json` unless the user explicitly asks for snapshot pinning.

### Node on PATH (Cursor Cloud VMs)

Cursor Cloud VMs ship **Node 22** on PATH ahead of nvm. `use_node_for_cursor_cloud` (in `.agents/scripts/cloud-install-lib.sh`) installs Node 24 and prepends nvm’s bin directory for the **install script** only. It also appends an `~/.bashrc` marker so **new interactive shells** prefer Node 24.

Non-interactive commands in the same agent turn (or before opening a fresh shell) may still run Node 22 unless you activate nvm:

```bash
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 24
export PATH="$(dirname "$(nvm which 24)"):$PATH"
```

Symptom: `node -v` shows v22 while `.nvmrc` requires 24 — `npm test` / native addons / `engines` checks fail mysteriously.

**Fleet edit guards:** `converge-repo.sh` wires three enforcement layers:

- **Cursor:** `merge-cursor-edit-guard.sh` adds `preToolUse` → `block-fleet-edits.sh` (denies `Write`/`Delete` on `.agents/**` and regenerated shims).
- **Claude Code:** `merge-claude-edit-guard.sh` merges `permissions.deny` for `Edit`/`Write` on the same paths into `.claude/settings.json`.
- **Codex:** advisory only — read `.agents/AGENTS.md` and `.agents/DO-NOT-EDIT.md`; no Codex config shipped (would override sandbox mode).

**Git guard hook:** `merge-cursor-git-guard.sh` wires `block-git-no-verify.sh` into `.cursor/hooks.json` (`beforeShellExecution`).

**Fleet freshness enforcement (three layers, all fail-only except cloud/shipping paths):**

| Layer | When | Behavior |
| --- | --- | --- |
| Cloud task start | Each cloud agent boot | `cloud-fleet-sync-if-stale.sh` pulls when stale (may stash/commit sync) |
| Pre-commit hook | Every local commit | `fleet-precommit-check.sh` **blocks** when stale — never auto-pulls |
| `/review-fix-push-babysit` step 1a | Before shipping app work | Explicit gate: stash if dirty, run `cloud-fleet-sync-if-stale.sh`, restore stash |

There is **no pre-push auto-sync**. Fix stale fleet with `./scripts/update-agents-subtree.sh` or let the cloud/shipping paths above run `cloud-fleet-sync-if-stale.sh`. During `/review-fix-push-babysit`, a named stash may appear briefly while fleet sync runs on a dirty tree — that is expected.

### Playwright browser E2E (opt-in)

Playwright 1.5x on Linux launches via **chrome-headless-shell**, not only the Chromium bundle. `npx playwright install chromium` alone leaves browser E2E failing with:

```text
Executable doesn't exist at .../chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell
```

Repos that run Playwright browser tests should call the fleet helper from `scripts/cloud-agent-install.sh` (after `npm ci` / `use_node_for_cursor_cloud`):

```bash
source "$(cd "$(dirname "$0")/.." && pwd)/.agents/scripts/cloud-install-lib.sh"
install_playwright_browsers_for_e2e   # installs chromium + chromium-headless-shell; verifies binary unless PLAYWRIGHT_E2E_VERIFY=0
```

Repos without Playwright E2E should **not** call this — it is not part of the default cloud install.

**Troubleshooting:** If install stalls at 100%, remove the stale lock and retry: `rm -f ~/.cache/ms-playwright/__dirlock`. If the binary is still missing, recover from the temp download: `unzip /tmp/playwright-download-*/*headless-shell*.zip -d ~/.cache/ms-playwright/` (then re-run the helper or `npx playwright install chromium-headless-shell`).

## Fleet updates (dotagents subtree)

Fleet config is vendored from [dotagents](https://github.com/jsolly/dotagents) `fleet` branch via [git subtree](https://gist.github.com/SKempin/b7857a6ff6bddb05717cc17a44091202).

**Pull latest fleet into this repo:**

```bash
./scripts/update-agents-subtree.sh
```

Or from a cloud task: `bash scripts/cloud-fleet-sync-if-stale.sh` (checks `FLEET.lock` first).

**Edit fleet canonical copy** (in `~/code/dotagents`, dotagents `main`):

```bash
cd ~/code/dotagents
# edit agents/, skills/, rules/, hooks/, templates/, or fleet scripts
git add <changed paths>
git commit -m "..."
git push   # CI rebuilds + publishes the fleet branch
```

Then sync into this repo via cloud task start or `update-agents-subtree.sh`.

**Note:** `.agents/` in this repo is **read-only** — pull-only. The `fleet` branch is published by dotagents CI from `~/code/dotagents`; editing `.agents/` here and pushing back upstream does not round-trip (the next CI publish overwrites it). Make fleet changes in `~/code/dotagents`.

### Secrets summary

| Secret | Where | Purpose |
| --- | --- | --- |
| `FLEET_SYNC_TOKEN` | Cursor Cloud repo secrets and GitHub Actions repo secret | Cloud agent fetch of `jsolly/dotagents` `fleet`; PR/push workflow `fleet-lock-guard` when `.agents/` changes |

Do **not** reuse `GH_AGENT_TOKEN` for fleet fetch — broader cross-repo scope; keep in Cursor-only config.

### FLEET.lock on pull requests

Repos with `.github/workflows/fleet-lock-guard.yml` verify when `.agents/` changes in a PR or push to `main`. `FLEET_SYNC_TOKEN` is required; the workflow fails closed without it.

1. `.agents/FLEET.lock` SHA matches `dotagents/fleet` HEAD (`FLEET_SYNC_TOKEN` required).
2. `.agents/` file blobs match the fleet tree at that SHA (content-drift check — catches hand-edits that keep a valid lock).

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
