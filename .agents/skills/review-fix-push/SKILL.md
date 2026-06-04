---
name: review-fix-push
description: Reviews local changes with parallel specialist agents, syncs main, fixes any blocking findings, pushes the result directly to main, and runs required post-push deploys (AWS SAM, Terraform, etc.) when project AGENTS.md path triggers match. Sole review gate — no PRs. Use when the user asks to push changes, says `/review-fix-push`, asks for "review and push" / "commit and push" / "ship it", or otherwise indicates they're ready to integrate local work to `main`. Do NOT invoke for routine in-flight commits — only when the user signals end-of-task integration.
effort: max
---

# Git Review, Fix, and Push to main

This is the sole review gate before code reaches the remote — there are no pull requests. **This skill always pushes to `main`.** Be thorough.

The expected starting state is one of two things:

- the user is on `main` directly with uncommitted/unpushed changes, or
- the user is in a worktree on a topic branch with uncommitted/unpushed changes that need to land on main.

Either way, the goal is the same: integrate, validate, push the result to `main`. Don't ask which branch to target — it's always `main`.

## Numbered orchestration

The orchestration is documented in `references/orchestration.md` — read it before each step. Summary:

1. **Inspect changes** — `git status`, `git diff`. → see `references/orchestration.md`
2. **Sync main into the working branch** — fetch, compare, merge or rebase, resolve conflicts. → see `references/orchestration.md` and `references/conflict-resolution.md`
3. **Load project guidelines + locate plan/spec** — read AGENTS.md files; locate `<repo-root>/docs/superpowers/plans/*.md` (or `docs/superpowers/specs/*.md`) for D.1 plan-injection per the specs-and-plans convention. → see `references/orchestration.md`
4. **Smoke check** — tests, type checker, CI reproduction via `act` if applicable. → see `references/orchestration.md` and `references/conflict-resolution.md`
5. **Architectural sanity check** — orchestrator notes structural concerns; these get injected into agent prompts via D.2. → see `references/orchestration.md`
6. **Review with parallel agents** — fan out always-run + extension-gated specialists. Agent fleet, gating rules, dispatch-prompt template are in `references/agent-fleet.md` and `references/dispatch-prompt.md`.
7. **Adjudicate findings with `confidence-scorer`** — drop Minor, score Critical/Important, drop adjudicated false positives and downgrades. → see `references/orchestration.md`
8. **Present verdict + findings** — verdict-line first, TL;DR paragraph, then per-severity findings. → see `references/orchestration.md`
9. **Fix issues + re-smoke** — fix all Critical and reasonable Important findings; re-run smoke (step 4) after fixes; loop up to 3 cycles total. → see `references/orchestration.md`
10. **Stage and commit** — stage by name (no `git add -A`); Conventional Commits message describing original intent. → see `references/orchestration.md`
11. **Push to main + worktree cleanup** — `git push origin HEAD:main`; pre-commit hooks must pass, never `--no-verify`. If the work was done in a worktree, default to switching back to `main`, fast-forwarding local `main`, and removing the worktree + topic branch. → see `references/orchestration.md`
12. **AWS / project deploys** — after push, match committed paths to AGENTS.md deploy rules; **run SAM/Terraform/etc. automatically** when triggered (not an optional follow-up). → see `references/deploy-rules.md`
13. **Final user summary** — after a successful push, lead with **`Pushed to main`** (commit SHA + summary), not the step-8 "Ready to push" review verdict. → see `references/orchestration.md` step 13

## Safety rules (non-negotiable)

- **Never push to a non-`main` branch** — this skill is for `main` only.
- **Never `--no-verify`** on commit or push. Per-agent guards in `.agents/hooks/` (see `references/safety-rules.md`) make this mechanical, not advisory.
- **Never `git push --force` / `--force-with-lease` / `git reset --hard`** — also blocked by deny rules.
- **Never `git add -A` or `git add .`** — stage by name to avoid sweeping in untracked secrets, large binaries, or probe artifacts.

## Cycle bound

The fix loop (step 9) is capped at 3 cycles total. On the 4th, surface the failure to the user and stop.

## Token economics

For small changes (a single file or two with trivial diffs), review inline without fanning out — agents are wasteful when there's nothing to find. Fan-out kicks in for diffs with multiple files or non-trivial logic changes. The skill is the gate; not every push needs the full fleet.

## Reference files

- `references/orchestration.md` — full step-by-step body, including D.1, D.2, D.3, E.1, E.2 wiring.
- `references/agent-fleet.md` — always-run + extension-gated tables, `model: inherit`, the `guidelines-auditor ×2` pattern.
- `references/output-contract.md` — canonical reviewer output schema (every agent inlines this).
- `references/dispatch-prompt.md` — the prompt template each agent receives via Task.
- `references/deploy-rules.md` — per-project post-commit deploy patterns (SAM, Terraform, Lambda code updates).
- `references/conflict-resolution.md` — merge conflict resolution + CI reproduction guidance.
- `references/safety-rules.md` — per-agent guards (Claude, Cursor, Codex) that mechanize the safety promise.
