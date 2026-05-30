# Orchestration — Full Step-by-Step

This is the operational body of `/review-fix-push`. The skill's `SKILL.md` is the dispatcher; this file holds the deep guidance for each step.

---

## 1. Inspect changes

- Run `git status`, `git diff`, and `git diff --cached` to see all local changes.
- After fetch (step 2), run `git diff --name-only origin/main...HEAD` to get the changed files for review.
- Note whether you're in a worktree: `git rev-parse --git-common-dir` and `git rev-parse --git-dir` differ in worktrees. The current branch may not exist on the remote, and the push target is `main` regardless of the current branch name.

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

- Read the project `AGENTS.md` (root of repo) and any linked guideline files it references (e.g., `.agents/code-style.md`, `.agents/testing.md`, etc.).
- Read any `AGENTS.md` in directories containing modified files.
- Read the global `.agents/AGENTS.md` for cross-project conventions.
- These guidelines are the standard the review is measured against.
- **Note any post-commit deploy rules** gated on specific paths (e.g., "SAM deploy required when `aws/template.yaml` changes", "run `terraform apply` after `infra/` changes"). These drive step 12.

**Plan/spec lookup (D.1)**:

Locate the plan or spec the user was implementing, in this order. Project-local paths are canonical — see `.agents/rules/specs-and-plans.md` for the full convention and why vendor-specific paths (`~/.claude/plans/`, etc.) are deprecated.

1. Most recently modified file matching `<repo-root>/docs/superpowers/plans/*.md` within the current session window. Resolve `<repo-root>` via `git rev-parse --show-toplevel` from the working directory.
2. Most recently modified file matching `<repo-root>/docs/superpowers/specs/*.md` (fallback if no plan exists but a spec does).
3. Any spec or plan path referenced explicitly in recent messages (e.g., the user pastes a path).
4. The conversation's first user message describing intent.
5. If none of the above produces content, set `{PLAN_OR_SPEC}` to the literal: `No explicit plan or spec — review against the diff and project guidelines only.`

Disambiguation: if multiple plans were modified within ~60 seconds of each other, pause and ask the user which to inject.

Legacy `~/.claude/plans/*.md` is intentionally not in the lookup chain — that location is deprecated per the specs-and-plans rule. If a user has plans lingering there, surface them in the message and ask whether to migrate to `docs/superpowers/plans/` before proceeding.

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

For larger changes, launch parallel agents simultaneously. Fleet composition (always-run + extension-gated), the `guidelines-auditor ×2` voting pattern, and per-agent model selection are documented in `references/agent-fleet.md`.

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

**Verdict line first** (E.1):

```text
**Verdict: <Ready to push / Needs attention / Needs work>**
<one-sentence reasoning>
```

Verdict thresholds:

- Any post-scoring Critical surviving → **Needs work**
- Any post-scoring Important surviving → **Needs attention**
- Otherwise → **Ready to push**

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

- `git push origin HEAD:main`. This works whether you're on `main`, on a worktree topic branch, or on any other local branch — the commits land on remote `main`.
- If the remote rejects the push as non-fast-forward, `main` advanced after the step-2 sync (rare but possible during a long review pass). Re-run step 2 against the new `origin/main`, re-run smoke checks, then push again.
- Pre-commit hooks run linting and tests automatically. If they fail, fix and re-commit. **Never use `--no-verify`** — per-agent guards (see `references/safety-rules.md`) block this mechanically.

### 11a. Worktree cleanup (default when work was done in a worktree)

If `git rev-parse --git-dir` differs from `git rev-parse --git-common-dir`, the work was done in a worktree. After a successful push, the default closing sequence is to switch back to `main` and remove the worktree — it existed to scope one piece of work, and that work is now in main. Run all four steps unless the user has signaled they want to keep iterating in the same worktree (e.g., a follow-up task explicitly tied to this branch).

1. **Switch the session back to the main checkout.** In Claude Code, call `ExitWorktree` with `action: "keep"` (the directory + branch survive on disk for the next two steps; the session's working directory returns to the main repo). Outside Claude Code, `cd` to the main repo path.
2. **Fast-forward the local `main` branch to include the just-pushed commit.** From the main checkout: `git fetch origin && git merge --ff-only origin/main` (or `git pull --ff-only origin main`). Skipping this leaves `main` behind `origin/main` and the next worktree session will redundantly re-merge the same commits.
3. **Remove the worktree directory.** From the main checkout: `git worktree remove <path>`. The command refuses if the worktree has uncommitted work — treat that as the safety check working, not as a problem to bypass; investigate whether that work was supposed to land in this push.
4. **Delete the topic branch.** `git branch -D <topic-branch>`. Safe because the commit is on `origin/main` — the branch ref is now redundant.

Confirm with the user only if you have positive signal they want to keep iterating in the same worktree. The default end-state is no worktree, on `main`, in sync with origin.

## 12. Project-specific deploys

See `references/deploy-rules.md` for the per-project deploy patterns and how to detect which apply.
