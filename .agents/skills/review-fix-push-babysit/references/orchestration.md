# Orchestration — Full Step-by-Step

This is the operational body of `/review-fix-push-babysit`. The skill's `SKILL.md` is the dispatcher; this file holds the deep guidance for each step.

---

## 1. Inspect changes

- Run `git status`, `git diff`, and `git diff --cached` to see all local changes.
- After fetch (step 2), run `git diff --name-only origin/main...HEAD` to get the changed files for review.
- Note whether you're in a worktree: `git rev-parse --git-common-dir` and `git rev-parse --git-dir` differ in worktrees. The current branch may not exist on the remote, and the push target is `main` regardless of the current branch name.

## 1a. Fleet freshness gate

**Read `references/fleet-sync-gate.md` first** — it holds the full procedure.

App repos with `.agents/FLEET.lock` must sync fleet **before** step 2's WIP commit. The fleet pre-commit guard blocks any commit when the lock is behind `dotagents/fleet`; running this gate here avoids hitting that guard mid-merge with uncommitted work still in the tree.

Summary:

1. If `.agents/FLEET.lock` is absent, skip — dotagents and non-fleet repos are not subtree consumers.
2. Run `bash .agents/scripts/fleet-precommit-check.sh` to detect current vs stale vs fetch failure.
3. When stale, run `./scripts/cloud-fleet-sync-if-stale.sh`. If the working tree is dirty, stash with `git stash push -u`, sync, then `git stash pop --index` per `references/fleet-sync-gate.md`.
4. Keep any `chore(fleet): …` sync commit on the branch being shipped.
5. On stash conflicts, fetch failures, or sync errors — **stop**; do not commit or push. Report recovery state (`git status`, stash list).
6. Re-run `git status` and continue to step 2.

Hooks remain fail-only — this gate is explicit sync on the shipping path, not pre-push auto-sync.

## 2. Sync main into the working branch

The review and tests below are only meaningful against the *merged* state — local feature work on a stale base is the most common source of regressions this skill needs to catch.

- `git fetch origin main`.
- Compare: `git rev-list --left-right --count HEAD...origin/main`. If the right-side count is 0, skip this step — the working branch already contains everything on `main`.
- Otherwise the working branch is behind `main`. Decide strategy:
  - **Default: merge.** `git merge origin/main`. Preserves the current commits and produces an explicit merge commit; conflict resolution happens once across the whole tree.
  - **Rebase** is appropriate only for small (1–2 commit) topic branches that haven't been pushed anywhere. Rewrites history and replays conflicts per commit. Don't default to it.
- **Before merging**: if there are uncommitted modifications, commit them as a topic commit first so the merge isn't fighting an unstaged diff. Use a Conventional Commits message that describes the work-in-progress (e.g., `feat(<scope>): <intent>` with a short body noting "WIP — staged before merging origin/main").
- **Conflicts**: see `references/conflict-resolution.md`.
- **After merging**: run typecheck + tests (step 4) before continuing. If the merge introduced regressions in test fixtures or signatures (common when upstream changed function signatures the topic branch's mocks rely on), fix them as part of the merge resolution, not as a follow-up commit.
- Commit the merge with the default merge message — Conventional Commits doesn't apply to merge commits.

This step is the gate that makes the rest of the skill meaningful. Skip it only if the working branch is already up to date with `main`.

## 3. Load project guidelines + locate plan/spec (D.1)

**Guidelines**:

- Read the project `AGENTS.md` (root of repo) and any linked guideline files it references (e.g., `.agents/rules/code-style.md`, `.agents/rules/testing.md`, etc.).
- Read any `AGENTS.md` in directories containing modified files.
- Read the active dotagents brief for cross-project conventions: on desktop, follow the installed entrypoint symlink (`~/.cursor/AGENTS.md` → `~/code/dotagents/AGENTS.md` or `AGENTS.work.md` per profile); in app repos, use `.agents/AGENTS.md`.
- These guidelines are the standard the review is measured against.
- **Capture post-push deploy rules** gated on specific paths — path prefixes, command, and preconditions (e.g., "SAM deploy required when `aws/template.yaml` or `src/handlers/` changes; command `npm run deploy:aws`; merge to main first when env vars change"). Record these as `{POST_PUSH_DEPLOYS}` for step 13. If none exist in AGENTS.md, set `{POST_PUSH_DEPLOYS}` to `none`.
- **Capture CI guard workflows** if AGENTS.md names specific workflows to wait on — record as `{CI_GUARD_WORKFLOWS}` for step 12. If none named, set to `all push-triggered`.

**Plan/spec lookup (D.1)**:

Locate the plan or spec the user was implementing, in this order. Project-local paths are canonical — see `rules/specs-and-plans.md` in the dotagents source or `.agents/rules/specs-and-plans.md` in app repos for the full convention and why vendor-specific planning directories are deprecated.

1. Most recently modified file matching `<repo-root>/docs/superpowers/plans/*.md` within the current session window. Resolve `<repo-root>` via `git rev-parse --show-toplevel` from the working directory.
2. Most recently modified file matching `<repo-root>/docs/superpowers/specs/*.md` (fallback if no plan exists but a spec does).
3. Any spec or plan path referenced explicitly in recent messages (e.g., the user pastes a path).
4. The conversation's first user message describing intent.
5. If none of the above produces content, set `{PLAN_OR_SPEC}` to the literal: `No explicit plan or spec — review against the diff and project guidelines only.`

Disambiguation: if multiple plans were modified within ~60 seconds of each other, pause and ask the user which to inject.

Legacy vendor-specific plan directories are intentionally not in the lookup chain. If a user has plans lingering outside the repo, surface that and ask whether to migrate them to `docs/superpowers/plans/` before proceeding.

The located plan text becomes `{PLAN_OR_SPEC}` in the dispatch prompt at step 6 — every agent will receive it under an `## Intended outcome` heading, with instruction to flag material divergence as Critical regardless of their lens.

## 4. Smoke check — tests, types, and CI reproduction

Before investing in agent review, verify the code works:

- Run the project's test command (e.g., `npm test`, `pytest`, `go test ./...`).
- Run the type checker if applicable (e.g., `tsc --noEmit`, `mypy`, `pyright`).
- If either fails, fix the failures first before proceeding to agent review.

**Reproduce CI locally when the change could affect it.** See `references/conflict-resolution.md` for the `act` reproduction guidance and the path-list that triggers it.

## 5. Architectural sanity check (D.2)

Before launching parallel agents, do a brief manual review of the diff for structural concerns that sub-agents aren't equipped to catch:

- **Wrong layer**: Is business logic leaking into handlers/controllers, or infrastructure concerns creeping into domain code?
- **Coupling**: Does this change introduce tight coupling between modules that were previously independent?
- **API surface**: Are new exports, endpoints, or public interfaces justified, or is this growing surface area unnecessarily?
- **Consistency**: Does the approach match how similar problems are solved elsewhere in the codebase?

Capture the orchestrator's notes — these become `{ARCHITECTURAL_NOTES}` in the dispatch prompt at step 6 (D.2). Each agent will receive your notes and is instructed not to re-flag what's already noted, only to corroborate or deepen the analysis.

If no concerns surfaced, set `{ARCHITECTURAL_NOTES}` to:

> No architectural concerns noted by the orchestrator. The change appears to fit existing patterns and respect module boundaries.

Don't leave it blank — agents read absent context as "not provided" and may compensate with extra paranoia.

## 6. Review with parallel agents

For small changes (a few files), review inline — no agents needed.

For larger changes, launch parallel agents simultaneously. Fleet composition (always-run + extension-gated), the `guidelines-auditor ×2` voting pattern, and `model: inherit` on all agents are documented in `references/agent-fleet.md`.

Each agent receives the dispatch prompt template from `references/dispatch-prompt.md` with these placeholders filled in:

| Placeholder | Source |
| --- | --- |
| `{PLAN_OR_SPEC}` | Located in step 3 (D.1) |
| `{ARCHITECTURAL_NOTES}` | Notes from step 5 (D.2) |
| `{GUIDELINES}` | Guidelines content from step 3 |
| `{CHANGED_FILES}` | `git diff --name-only origin/main...HEAD` |
| `{DIFF}` | `git diff origin/main...HEAD` |

Expect 15–30 total Task calls per invocation including the `confidence-scorer` pass in step 7.

Each agent returns findings in the canonical contract format (see `references/output-contract.md`): Critical/Important/Minor + verdict line + ≤10 findings.

## 7. Adjudicate findings with `confidence-scorer`

Collect every finding from step 6 (including architectural concerns from step 5). For each Critical or Important finding, invoke `confidence-scorer` in a fresh sub-agent call with only:

- The finding text and asserted severity.
- The relevant file excerpt.
- The diff hunk.

Do NOT include the originating agent name or its reasoning — independence is the design.

The scorer returns one of:

- **Confirm Critical** — keep as Critical.
- **Confirm Important** — keep as Important.
- **Downgrade to Important** — move from Critical to Important bucket.
- **Downgrade to Minor** — drop from the report.
- **False positive** — drop from the report.

Drop all Minor findings from the report before scoring (the scorer doesn't see them at all). Also drop findings catchable by tooling (Biome, tsc, test suite) even if they're confirmed — CI and pre-commit hooks will surface those.

Run scorer calls in parallel where possible — one Task call per finding, never batched (batching lets earlier scores anchor later ones). After scoring, dedupe surviving findings by `(file, line, issue)` — the duplicated `guidelines-auditor` will naturally produce overlapping findings.

## 8. Present verdict + findings (E.1, E.2)

**Pre-push review verdict** — use at step 8 only, before commit/push. Do **not** reuse this wording in the final summary after a successful ship (see step 14).

**Verdict line first** (E.1):

```text
**Review verdict: <Ready to push / Needs attention / Needs work>**
<one-sentence reasoning>
```

Verdict thresholds:

- Any post-scoring Critical surviving → **Needs work**
- Any post-scoring Important surviving → **Needs attention**
- Otherwise → **Ready to push**

If the verdict is **Needs work** or **Needs attention**, stop after presenting findings — do not commit or push until issues are fixed (step 9) and the verdict is **Ready to push**.

**TL;DR paragraph** (E.2):

A 2–3 sentence summary: *"3 critical issues across `auth/handlers.ts:42` and `db/migrate.sql:18`; 2 important suggestions; tests pass; ready for fix-and-retry."* This is the headline — the user reads this first.

**Findings list** — group by severity (Critical / Important / Minor), retaining the per-finding 4-field shape:

- **File:line**
- **What**
- **Why it matters**
- **Fix**

Surface architectural notes from step 5 alongside the agent findings.

## 9. Fix issues + re-smoke (D.3)

- Fix all **Critical** issues and reasonable **Important** issues. Explain each fix.
- Skip suggestions that are debatable or require refactoring beyond scope — note why.
- **Re-run smoke checks (step 4) after fixes** before committing. Fixes themselves can break things — especially refactor-style fixes that touch multiple call sites. No commit without green smoke.
- Re-review (step 6 + 7) after fixing if any Critical issues remain. Repeat until no Critical issues remain.

**Loop bound**: 3 cycles total (matches the existing fix-loop bound). On the 4th, surface the failure to the user and stop. Don't push with unresolved Critical findings.

## 10. Stage and commit

- Stage changes by name (avoid `git add -A` if secrets or binaries may be present).
- Commit with a Conventional Commits message: `type(scope): summary` (under ~72 chars).
- The message should describe the **original intent**, not the review fixes.
- Examples: `feat(prefs): add timezone fetch and mismatch banner`, `fix(api): validate timezone before update`

## 11. Push to main

The destination is always `main`. The current branch name doesn't matter — the goal is to advance `main` to the current HEAD.

**Before pushing:** if `.github/workflows/` exists and the remote is GitHub, verify `gh auth status` and `gh workflow list`. If `gh` is not authenticated, stop and ask the user to run `gh auth login` — do not push and then discover babysit is impossible.

- `git push origin HEAD:main`. This works whether you're on `main`, on a worktree topic branch, or on any other local branch — the commits land on remote `main`.
- If the remote rejects the push as non-fast-forward, `main` advanced after the step-2 sync (rare but possible during a long review pass). Re-run step 2 against the new `origin/main`, re-run smoke checks, then push again.
- Pre-commit hooks run linting and tests automatically. If they fail, fix and re-commit. **Never use `--no-verify`** — per-agent guards (see `references/safety-rules.md`) block this mechanically.

**Do not run worktree cleanup here.** CI babysit (step 12) may require additional fix/push cycles from the same checkout. Worktree cleanup is deferred to step 15.

## 12. CI babysit (post-push)

**Read `references/ci-babysit.md` first** — it holds the full procedure.

Summary:

1. If no `.github/workflows/`, skip and note `CI: skipped (no workflows)`; proceed to step 13.
2. Capture `SHA=$(git rev-parse HEAD)` and list push-triggered runs via `gh run list --commit "$SHA"`.
3. Watch all push-triggered runs (or `{CI_GUARD_WORKFLOWS}` from step 3) with `gh run watch --exit-status`.
4. On failure: inspect `gh run view <run-id> --log-failed`, fix locally, smoke, commit (`fix(ci): …`), push, re-watch new SHA.
5. **Loop bound:** 3 CI fix cycles, ~45-minute wall-clock ceiling. On the 4th failure, stop and report — do not claim shipped.
6. On non-fast-forward during babysit: re-run step 2 sync, smoke, push, then re-watch.

Do not weaken CI, skip hooks, or make unrelated changes to turn CI green.

## 13. AWS / project deploys (post-CI)

Shipping is not complete until required deploys run. Step 11 puts code on `main`; step 12 verifies CI; step 13 pushes that code to runtime (Lambdas, infra, images) when project rules say so.

**Manual deploys run only after step 12 CI green (or CI skipped).** Do not run SAM/Terraform when CI is red.

**Read `references/deploy-rules.md` first** — especially the **AWS SAM** section when the repo has an `aws/` stack.

### Detect

1. Use `{POST_PUSH_DEPLOYS}` captured in step 3 (from AGENTS.md, `docs/deploy-gotchas.md`, linked deploy docs).
2. List files in the push: `git diff --name-only origin/main~1 HEAD` (single commit) or `git diff --name-only origin/main...HEAD` (multi-commit push).
3. If any committed path matches a documented trigger prefix, a deploy is **required** — not a suggestion for the user to run later.

### Execute

1. Announce before each deploy: `Running <command> because <matched paths> changed`.
2. **AWS SAM** (when triggers match — see deploy-rules.md):
   - Push to `main` must already have succeeded (step 11) and CI must be green (step 12).
   - Prefer repo-root script when defined: `npm run deploy:aws`. Otherwise: `cd aws && npm run deploy` (or the command AGENTS.md names).
   - Use the project's AWS profile (`AWS_PROFILE` in AGENTS.md / `docs/tooling-setup.md`). If output shows SSO/token expiry, **stop** and ask the user to `aws sso login` — do not retry with a different profile.
   - Stream full deploy output. On failure: report the error, note that `main` is updated but Lambdas/infra may be stale, and **do not** claim the skill finished successfully.
3. **Other stacks** (Terraform, CDK, Docker push): run the command from `{POST_PUSH_DEPLOYS}` / deploy-rules.md. Confirm with the user first when the deploy is destructive (prod DDL, teardown).
4. If no trigger paths matched, skip step 13 silently.

### Record for step 14

Note deploy outcome in the closing summary: `AWS SAM deploy: succeeded` / `skipped (no trigger paths)` / `failed — <reason>`.

## 14. Final user summary (E.3)

After steps 10–13 complete, send **one closing message** to the user. This is separate from the step-8 review verdict — the user should never finish the skill wondering whether the push happened.

**Lead with outcome, not review status:**

| Outcome | Opening line |
| --- | --- |
| Full success (CI green + deploys OK) | **`Shipped to main`** — SHA, CI green, deploy outcome |
| Push OK, CI green, no deploy needed | **`Shipped to main`** — `deploy: skipped (no triggers)` |
| Push OK, CI exhausted | **`Pushed to main — CI failed (stopped)`** — last failure, cycles used |
| Push OK, CI green, deploy failed | **`Pushed to main — deploy failed`** — CI OK, runtime may be stale |
| Push failed | **`Push failed`** — error summary and next step |
| Stopped on findings | **`Stopped — not pushed`** — reference the step-8 review verdict |
| CI skipped (no workflows) | **`Shipped to main`** — note `CI: no workflows` |

Then: TL;DR of the change, checks run (tests/lint), CI babysit cycles count, deploy notes, and unresolved Important findings if you pushed despite them (should be rare).

**Do not** end a successful run with **"Ready to push"** or **"Review verdict: Ready to push"** — that language is pre-push gate only and reads as if nothing landed on the remote.

## 15. Worktree cleanup (deferred from old step 11a)

If `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, the work was done in a worktree. After step 12 finishes (green or stopped on cycle cap) and step 13 runs or is skipped, the default closing sequence is to switch back to `main` and remove the worktree — even when CI failed or deploy failed, unless the user wants to keep fixing in the worktree. Run all four steps unless the user has signaled they want to keep iterating in the same worktree.

1. **Switch the session back to the main checkout.** In Claude Code, call `ExitWorktree` with `action: "keep"` (the directory + branch survive on disk for the next two steps; the session's working directory returns to the main repo). Outside Claude Code, `cd` to the main repo path.
2. **Fast-forward the local `main` branch to include the just-pushed commit.** From the main checkout: `git fetch origin && git merge --ff-only origin/main` (or `git pull --ff-only origin main`). Skipping this leaves `main` behind `origin/main` and the next worktree session will redundantly re-merge the same commits.
3. **Remove the worktree directory.** From the main checkout: `git worktree remove <path>`. The command refuses if the worktree has uncommitted work — treat that as the safety check working, not as a problem to bypass; investigate whether that work was supposed to land in this push.
4. **Delete the topic branch.** `git branch -D <topic-branch>`. Safe because the commit is on `origin/main` — the branch ref is now redundant.

Confirm with the user only if you have positive signal they want to keep iterating in the same worktree. The default end-state is no worktree, on `main`, in sync with origin.
