# Dispatch Prompt Template

This is the template the orchestrator (`/review-fix-push-babysit`) uses when invoking each reviewer subagent via the `Task` tool. The orchestrator fills the placeholders before dispatching.

The template ensures every agent receives:

- The intent of the change (plan/spec) — D.1
- The orchestrator's own architectural notes — D.2
- The diff, changed files, and full contents of changed files (for boundary and file-size analysis)
- Project guidelines

Without these, agents review against generic principles instead of *this* change's specific intent. The plan injection (D.1) is the single largest expected lift in review quality.

---

## Template

```markdown
## Intended outcome

{PLAN_OR_SPEC}

If the diff materially diverges from the intended outcome — under-implements, over-scopes, or contradicts the spec — report it as Critical regardless of your usual lens.

## Architectural notes from orchestrator

{ARCHITECTURAL_NOTES}

Don't re-flag what's already noted; you may corroborate or deepen the analysis.

## Project guidelines

{GUIDELINES}

## Changed files

{CHANGED_FILES}

## Changed file contents

{FILE_CONTENTS}

Full file bodies for every path in changed files — not just diff hunks. Use for file-size boundaries, cross-hunk context, and module-boundary analysis.

## Diff

{DIFF}

---

Review per your declared scope. Follow the output contract in your system prompt.
```

## Placeholder resolution

| Placeholder | Source | Fallback |
| --- | --- | --- |
| `{PLAN_OR_SPEC}` | Most recently modified `<repo-root>/docs/superpowers/plans/*.md` within the session, falling back to `<repo-root>/docs/superpowers/specs/*.md`, or a path referenced explicitly in recent messages. See `references/orchestration.md` step 3 and `rules/specs-and-plans.md` in dotagents (`.agents/rules/specs-and-plans.md` in app repos). | Use the conversation's first user message describing intent. If none, write `No explicit plan or spec — review against the diff and project guidelines only.` |
| `{ARCHITECTURAL_NOTES}` | The orchestrator's notes from step 5 (architectural sanity check) | `No architectural concerns noted.` |
| `{GUIDELINES}` | Concatenated content of project root `AGENTS.md`, any `AGENTS.md` in directories containing modified files, and the active dotagents brief (desktop: read `~/.cursor/AGENTS.md` symlink target; app repos: `.agents/AGENTS.md`) | The user's active dotagents brief alone if no project `AGENTS.md` exists |
| `{CHANGED_FILES}` | Union of committed branch changes (`origin/main...HEAD`), staged changes, unstaged changes, and untracked files | Required — must not be empty |
| `{FILE_CONTENTS}` | Full text of each changed file, labeled by path (orchestrator reads via the file-read tool in step 6) | Required for fan-out — use `(deleted)` for removed paths, `(binary — skipped)` for non-text |
| `{DIFF}` | Combined committed branch diff, staged diff, unstaged diff, and untracked-file markers | Required — must not be empty |

## When to skip placeholder injection

For agents that already have everything they need from their system prompt and don't benefit from plan/sanity context:

- `confidence-scorer` — gets only the finding, file excerpt, and diff hunk per its existing contract. Does NOT receive `{PLAN_OR_SPEC}` or `{ARCHITECTURAL_NOTES}`. Independence is the design.

For all 16 other agents, dispatch with the full template above.

## Disambiguating multiple plans

If `<repo-root>/docs/superpowers/plans/` has multiple files modified within the session window:

1. **Default**: pick the most recently modified.
2. **If ambiguous** (two files modified within 60 seconds of each other), pause and ask the user which to use as `{PLAN_OR_SPEC}`.
3. **If no plans exist**: fall through to the spec dir, then to recent-message-referenced paths, then to the conversation's first user message describing intent, then to the literal sentinel.

## Empty `{ARCHITECTURAL_NOTES}` handling

If the orchestrator's step 5 finds no concerns, `{ARCHITECTURAL_NOTES}` should be set to:

```text
No architectural concerns noted by the orchestrator. The change appears to fit existing patterns and respect module boundaries.
```

Don't leave it blank — agents read absent context as "not provided" and may compensate with extra paranoia.
