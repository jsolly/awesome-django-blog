---
name: review-fix
description: Reviews local changes with parallel specialist agents and applies fixes for blocking findings, stopping BEFORE commit (no staging, no push). Optional natural-language argument scopes the review to one concept — e.g., `/review-fix the plan` reviews only files matching "the plan" in the diff. Use this skill whenever the user says `/review-fix`, asks to "review and fix" / "review my changes and fix the issues" / "do a review pass and patch what's broken", asks for a "code review pass" before they commit, or wants critical findings cleaned up while still deciding whether to commit. Do NOT invoke when the user is already ready to push (use `review-fix-push`) or wants a read-only review with no fixes (use `review` or `security-review`).
effort: max
---

# Local Review + Fix (no commit, no push)

This skill is the mid-flight cousin of `/review-fix-push`. Same review fleet, same fix loop — but it stops before staging anything. After it runs, fixes live in the working tree as uncommitted changes; the user decides whether and when to commit.

The expected starting state is one of two things:

- the user is on `main` directly with uncommitted/unpushed changes, or
- the user is in a worktree on a topic branch with uncommitted/unpushed changes.

Where those changes ultimately land doesn't matter — this skill never pushes and never commits.

## Optional argument: concept-only scope

`/review-fix` (no argument) reviews **all** changed files since `origin/main`.

`/review-fix <natural-language description>` scopes the review to files matching that description. The argument is **always interpreted as a concept**, never as a literal path or glob. If the user types `/review-fix src/auth/`, treat `src/auth/` as a concept ("the auth changes") and resolve through the diff — don't shell-glob it.

Resolution procedure:

1. List candidates: `git diff --name-only origin/main...HEAD`.
2. Match the concept against candidates using filename + path semantics. Examples:
   - `the plan` → files matching `*plan*.md`, `~/.claude/plans/*.md`, `docs/superpowers/specs/*.md`, `docs/**/plan*.md`
   - `the migration` → files under `supabase/migrations/`, `migrations/`, or any new `*.sql` files
   - `the auth changes` → files with `auth` anywhere in the path
   - `the Vue dashboard` → files under `src/components/dashboard/**/*.vue`
3. Show the matched scope as a 1-line summary (e.g., `Scoped to: 2 files in supabase/migrations/`) and proceed.
4. Ambiguity rules:
   - **0 matches** → tell the user, offer to fall back to reviewing the full diff, wait for confirmation. Don't silently widen the scope.
   - **Matches but unclear** (concept could plausibly mean two non-overlapping subsets) → show the candidates and ask which they meant.

When scoped, the `{CHANGED_FILES}` and `{DIFF}` passed to agents are restricted to the scoped subset. The plan/spec injection (D.1) and architectural pass (D.2) still run, but they're framed against the scope, not the full diff.

## Numbered orchestration

The full body is in `references/orchestration.md` — read it before each step. Summary:

1. **Resolve scope** — parse the argument (if any), match against the diff, confirm with the user. → see `references/orchestration.md`.
2. **Inspect changes** — `git status`, `git diff` over the scoped files.
3. **Sync main into the working branch** — fetch, compare, merge or rebase, resolve conflicts. Identical to `/review-fix-push` step 2. → see `.agents/skills/review-fix-push/references/orchestration.md` and `.agents/skills/review-fix-push/references/conflict-resolution.md`.
4. **Load project guidelines + locate plan/spec** — D.1 plan injection (same as `/review-fix-push`). → see `.agents/skills/review-fix-push/references/orchestration.md` step 3.
5. **Smoke check** — tests, type checker, CI reproduction via `act` if applicable.
6. **Architectural sanity check** — orchestrator notes for D.2.
7. **Review with parallel agents** — fleet, dispatch prompt, output contract are shared with `/review-fix-push`. → see `.agents/skills/review-fix-push/references/agent-fleet.md`, `.agents/skills/review-fix-push/references/dispatch-prompt.md`, `.agents/skills/review-fix-push/references/output-contract.md`.
8. **Adjudicate findings with `confidence-scorer`** — drop Minor, score Critical/Important, drop adjudicated false positives and downgrades.
9. **Present verdict + findings** — verdict-line first, TL;DR paragraph, then per-severity findings.
10. **Fix issues + re-smoke** — fix all Critical and reasonable Important findings; re-run smoke (step 5) after fixes; loop up to 3 cycles total.
11. **Stop and report** — show `git status` plus a one-line summary of what changed in the working tree; explicitly remind the user nothing was committed and suggest `/review-fix-push` when they're ready to ship.

## Safety rules (non-negotiable)

- **Never stage, commit, or push.** This skill ends with changes uncommitted in the working tree. The only allowed `git add` is the one needed to resolve a merge conflict during step 3 — and only for the conflict markers.
- **Never `--no-verify`** — inherited from the project's deny rules; not relevant here since no commits happen.
- **Never `git push --force` / `--force-with-lease` / `git reset --hard`** — blocked by deny rules.
- **Never `git add -A` or `git add .`** — and in this skill, never `git add` at all outside merge resolution.

## Cycle bound

The fix loop (step 10) is capped at 3 cycles total. On the 4th, surface what remains as still-Critical and stop. Hand control back to the user — don't keep grinding, and don't downgrade severity to escape the loop.

## Token economics

For small scoped reviews (a single file or two with trivial diffs), review inline without fanning out — agents are wasteful when there's nothing to find. Fan-out kicks in for diffs with multiple files or non-trivial logic changes. Scoped invocations skew small by design, so inline review is the common path when an argument is provided.

## Reference files

- `references/orchestration.md` — full step-by-step body, including scope resolution and the differences from `/review-fix-push`.
- Shared with `/review-fix-push` (read directly from there):
  - `.agents/skills/review-fix-push/references/agent-fleet.md` — always-run + extension-gated agent tables, model rationale, the `guidelines-auditor ×2` pattern.
  - `.agents/skills/review-fix-push/references/dispatch-prompt.md` — prompt template each agent receives via Task.
  - `.agents/skills/review-fix-push/references/output-contract.md` — canonical reviewer output schema.
  - `.agents/skills/review-fix-push/references/conflict-resolution.md` — merge conflict resolution + CI reproduction.
  - `.agents/skills/review-fix-push/references/safety-rules.md` — `permissions.deny` rules in settings.json.
