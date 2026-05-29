---
description: Where specs and plans live — docs/superpowers/, not vendor paths
alwaysApply: true
---

# Specs & Plans

Specs and implementation plans live inside the project repo, not in vendor-specific paths. Anchoring planning artifacts to whatever editor or agent we happen to be using today (`~/.claude/`, `~/.cursor/`, `~/.gemini/`) makes the work fragile to tool changes and invisible to teammates browsing the repo on GitHub.

## Locations

| Artifact | Path | Filename |
| --- | --- | --- |
| Design / spec | `<repo>/docs/superpowers/specs/` | `YYYY-MM-DD-<slug>-design.md` |
| Implementation plan | `<repo>/docs/superpowers/plans/` | `YYYY-MM-DD-<slug>.md` |

- **Slug**: kebab-case, descriptive (`extended-hours-notifications`, `spec-compliance-reviewer`). No spaces, no random word-tuples.
- **Date**: the day work begins (or the design lands), not the day it ships. Don't backfill.
- **Working on `.agents/` itself?** Treat it as a child repo — artifacts go to `.agents/docs/superpowers/{specs,plans}/`.

## Two-file pattern

- **Spec (`-design.md`)**: what we want and why. Goal, problem, requirements, acceptance criteria, alternatives considered, open questions. Long-form where useful. Self-contained — no implementation steps.
- **Plan (no suffix)**: how to build it. TDD-driven tasks with concrete steps, file paths, commands, expected outputs. Per `superpowers:writing-plans`. The plan opens with `**Spec:** docs/superpowers/specs/<spec-file>.md` so the implementer reads them together.

A small change can collapse to a single plan file with a brief inline "Spec" section. Most non-trivial work justifies two files because the spec is approved separately and outlives any one implementation attempt.

## Cross-references

- The plan references the spec (`**Spec:** docs/superpowers/specs/...`).
- The eventual commit / PR description references the plan (`Implements docs/superpowers/plans/...`) so reviewers can audit the work against the intent.
- The `/review-fix-push` orchestrator's D.1 spec lookup should find these files automatically (see "Discovery", below).

## Don't use

- ❌ `~/.claude/plans/`, `~/.claude/specs/` — vendor lock-in; not in the project's git history; invisible to GitHub-only contributors.
- ❌ `~/.cursor/`, `~/.gemini/`, etc. — same problem in a different costume.
- ❌ Top-level `plans/` or `specs/` directories without the `docs/superpowers/` prefix — okay-ish for tiny solo projects but breaks discoverability across the fleet of repos that DO follow the convention.

## Naming examples

✅ `docs/superpowers/specs/2026-05-10-markdown-linter-design.md`
✅ `docs/superpowers/plans/2026-05-23-spec-compliance-reviewer.md`
❌ `plans/markdown-linter.md` (no date, no `docs/superpowers/` prefix)
❌ `docs/plans/squishy-conjuring-lobster.md` (random slug, no date)
❌ `~/.claude/plans/2026-05-23-spec-compliance-reviewer.md` (vendor lock-in)

## Discovery for `/review-fix-push`

The `/review-fix-push` orchestrator's plan lookup at step 3 (D.1) follows this rule. The lookup order, per `.agents/skills/review-fix-push/references/orchestration.md`:

1. `<repo-root>/docs/superpowers/plans/*.md` (most recently modified within the session)
2. `<repo-root>/docs/superpowers/specs/*.md` (fallback if no plan but a spec exists)
3. Any spec/plan path referenced explicitly in recent messages
4. The conversation's first user message describing intent
5. The literal "no spec" sentinel: `No explicit plan or spec — review against the diff and project guidelines only.`

`<repo-root>` is resolved via `git rev-parse --show-toplevel` from the orchestrator's working directory. The deprecated `~/.claude/plans/*.md` is intentionally absent — if you have plans there, the orchestrator will surface them and ask whether to migrate.
