# Orchestration — Full Step-by-Step

This is the operational body of `/review-fix`. The skill's `SKILL.md` is the dispatcher; this file holds the deep guidance for each step. Where the mechanics are identical to `/review-fix-push`, this file points at that skill's reference rather than duplicating — the goal is one source of truth for the agent fleet, dispatch prompt, output contract, and conflict resolution.

The big difference from `/review-fix-push`: this skill **stops at step 11** (report-and-stop). No staging, no commit, no push, no deploy. Treat that as load-bearing — don't drift back into the push flow even if the verdict comes back clean.

---

## 1. Resolve scope

The slash-command may arrive with an argument (`/review-fix the plan`) or without (`/review-fix`). The argument is **always a concept**, never a literal path or glob — even if it looks path-like.

If no argument: scope is the full diff. Skip to step 2.

If an argument is present:

1. List candidates: `git diff --name-only origin/main...HEAD` (run after the fetch in step 3 if you haven't already; for the first pass, `git diff --name-only HEAD` against the local working tree is fine — you'll re-resolve after sync).
2. Match the concept using filename + path semantics. Use these heuristics in order:
   - Direct token match in the path (`auth` → any path containing `auth`).
   - File-type cluster (`migration` → `*.sql` files; `plan` / `spec` → `*.md` under `docs/superpowers/plans/`, `docs/superpowers/specs/`, or project-local docs paths).
   - Directory cluster (`dashboard` → all files under `src/components/dashboard/`).
   - If none of the above produces a confident match and the diff is small (≤5 files), sample the contents of each and judge by the file's own stated purpose.
3. Show the matched scope as a single line: `Scoped to: <N> file(s) — <one-line summary>`.
4. Resolve ambiguity:
   - **0 matches** → tell the user no files matched, offer to fall back to the full diff, wait for confirmation. Do not silently widen the scope; the whole point of an argument is the user wanted narrowing.
   - **Multiple plausible interpretations** → list candidates with a brief rationale and ask which set the user meant. Don't guess between non-overlapping subsets.
   - **Single confident match** → proceed without confirmation but with the scope summary visible.

The resolved scope becomes the basis for `{CHANGED_FILES}` and `{DIFF}` in step 7. The plan/spec injection (D.1) and architectural notes (D.2) still run, but they're framed against the scope, and the agents are told the diff has been narrowed by user intent — see step 7 for the wiring.

## 2. Inspect changes

- `git status` and `git diff` to see the working-tree state.
- `git diff --cached` if there are staged changes (rare here, but possible if the user staged manually).
- `git rev-parse --git-common-dir` and `git rev-parse --git-dir` to detect a worktree.
- If scoped (step 1), filter to only the scoped paths when displaying or running diffs (`git diff -- <paths>`).

## 3. Sync main into the working branch

Identical to `/review-fix-push` step 2 — `git fetch origin main`, compare, merge (default) or rebase (1–2 commit topic branches only), resolve conflicts, re-run smoke before continuing.

Read `.agents/skills/review-fix-push/references/orchestration.md` step 2 for the full procedure, and `.agents/skills/review-fix-push/references/conflict-resolution.md` for conflict guidance.

The user picked "still sync main" for this skill because reviewing on a stale base produces the same false-confidence pattern that the push gate catches. Don't skip it.

After sync, re-resolve scope (step 1) against the post-merge diff: `git diff --name-only origin/main...HEAD`. If the scoped set changed (merge added files matching the concept, or removed some), surface the new set to the user before proceeding.

**One difference from the push variant**: if the sync introduces a merge commit, that commit *will* exist locally even though this skill doesn't push. That's fine and expected — the user can decide later (via `/review-fix-push` or manual push) whether the merge ships. The merge commit is the cost of reviewing against the merged state. Don't try to undo it; don't reset back.

## 4. Load project guidelines + locate plan/spec (D.1)

Identical to `/review-fix-push` step 3. Read `.agents/skills/review-fix-push/references/orchestration.md` step 3 for the full procedure.

Quick recap:

- Read project `AGENTS.md` (root of repo) + linked guideline files + global `.agents/AGENTS.md`.
- Locate the plan or spec the user was implementing (most-recent `<repo-root>/docs/superpowers/plans/*.md`, then `<repo-root>/docs/superpowers/specs/*.md`, then a path referenced in recent messages, then the conversation's first user message). See `rules/specs-and-plans.md` in the dotagents source or `.agents/rules/specs-and-plans.md` in app repos.
- Note any post-commit deploy rules — but in this skill they're informational only (we don't deploy here).

The located plan text becomes `{PLAN_OR_SPEC}` in the dispatch prompt at step 7.

## 5. Smoke check — tests, types, and CI reproduction

Same as `/review-fix-push` step 4. Run the project's test command, the type checker, and `act` for CI reproduction when relevant paths changed (see `.agents/skills/review-fix-push/references/conflict-resolution.md`).

If smoke fails, fix those failures before proceeding to agent review — same gate as the push variant. A red baseline makes the agent review noisy because every reviewer will spot the breakage independently.

## 6. Architectural sanity check (D.2)

Same as `/review-fix-push` step 5 — orchestrator-side manual scan for wrong-layer logic, coupling, API surface bloat, and inconsistency with existing patterns. Capture notes for `{ARCHITECTURAL_NOTES}` in the dispatch prompt. If nothing surfaces, set the placeholder to the explicit "no concerns noted" string — never leave it blank.

## 7. Review with parallel agents

Same fleet, same dispatch template, same output contract as `/review-fix-push` step 6. Read:

- `.agents/skills/review-fix-push/references/agent-fleet.md` — always-run + extension-gated agents, model rationale, `guidelines-auditor ×2` pattern.
- `.agents/skills/review-fix-push/references/dispatch-prompt.md` — prompt template.
- `.agents/skills/review-fix-push/references/output-contract.md` — reviewer output schema.

Placeholder fill-ins:

| Placeholder | Source |
| --- | --- |
| `{PLAN_OR_SPEC}` | Located in step 4 (D.1) |
| `{ARCHITECTURAL_NOTES}` | Notes from step 6 (D.2) |
| `{GUIDELINES}` | Guidelines content from step 4 |
| `{CHANGED_FILES}` | `git diff --name-only origin/main...HEAD`, **filtered to the scoped subset if step 1 narrowed it** |
| `{DIFF}` | `git diff origin/main...HEAD -- <scoped paths>` if scoped, else `git diff origin/main...HEAD` |

**Scoped-mode addendum to the dispatch prompt**: when the review is scoped, append one paragraph to the dispatch prompt under a heading like `## Scope` telling the agents that the user explicitly narrowed the review to this concept (`<concept>`) and they should not flag findings in files outside this set, even if they appear in the merge base. This prevents the fleet from spending tokens on out-of-scope hunches.

For small scoped diffs (1–2 files, trivial changes), skip the fan-out — review inline. The fleet is overkill when there's almost nothing to find, and the user invoked a scoped review precisely because they wanted a tight, focused pass.

## 8. Adjudicate findings with `confidence-scorer`

Same as `/review-fix-push` step 7. Drop Minor before scoring; run scorer in parallel, one Task per finding, never batched (batching anchors later scores to earlier ones); drop adjudicated false positives and Minor downgrades; dedupe surviving findings by `(file, line, issue)`.

Findings catchable by tooling (Biome, tsc, the test suite) drop out the same way — but be aware that since this skill doesn't commit, those tools haven't yet had their pre-commit-hook turn. If the user runs `/review-fix-push` next, those will surface there. Don't re-flag them here.

## 9. Present verdict + findings (E.1, E.2)

Same shape as `/review-fix-push` step 8 — verdict line, TL;DR paragraph, per-severity findings list with the 4-field shape (file:line, what, why it matters, fix). Surface architectural notes alongside agent findings.

**Verdict thresholds** (adjusted for the no-push outcome):

- Any post-scoring Critical surviving → **Needs work** (will enter the fix loop in step 10).
- Any post-scoring Important surviving → **Needs attention** (will be fixed if reasonable, in step 10).
- Otherwise → **Clean** (skip step 10, go directly to step 11).

The `Ready to push` verdict from `/review-fix-push` doesn't apply here — this skill never pushes. Use `Clean` for the no-issues case.

## 10. Fix issues + re-smoke (D.3)

Same as `/review-fix-push` step 9.

- Fix all **Critical** issues and reasonable **Important** issues. Explain each fix as you make it.
- Skip suggestions that are debatable or require refactoring beyond scope — note why.
- **Re-run smoke (step 5) after fixes** before declaring done. Fixes can break things, especially refactor-style fixes that touch multiple call sites.
- Re-review (step 7 + 8) after fixing if any Critical issues remained. Repeat until no Critical issues remain or the cycle bound is hit.

**Loop bound**: 3 cycles total. On the 4th, surface what's still Critical, stop, and skip to step 11 with a clear "still has unresolved Critical findings" note. Do not downgrade severity to escape the loop. Do not stage or commit partial fixes. The user picked "Surface and stop" for stuck Criticals during skill setup — honor that.

## 11. Stop and report

This is where this skill ends. The intent is to leave the working tree in a clean, reviewable state with all the agent-applied fixes present but uncommitted, so the user can inspect, iterate, or hand off to `/review-fix-push`.

Output, in this order:

1. **One-line outcome**: one of
   - `Clean — no Critical or Important findings; smoke passed.`
   - `Fixed — N findings resolved across <files>; smoke passed.`
   - `Partial — N fixed, M still Critical (cycle bound hit); smoke passed.` (or `smoke failed` — surface that loud)
2. **`git status`** output, verbatim, so the user sees exactly what's uncommitted.
3. **A short summary line** of what changed in the working tree relative to the pre-skill state (e.g., `2 files modified by fixes; 1 merge commit added by sync`).
4. **Next-step nudge**: explicitly remind the user that nothing was committed and suggest `/review-fix-push` when they're ready to ship. If the verdict was `Partial`, suggest the user resolve the remaining Critical findings manually before running `/review-fix-push`, since that skill will re-flag them.

Do not run `git add`, `git commit`, `git push`, or any deploy commands. The merge commit from step 3 is the only commit this skill is allowed to create, and it was created as part of conflict resolution — not as part of finishing.
