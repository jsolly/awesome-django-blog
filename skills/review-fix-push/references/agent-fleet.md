# Agent Fleet — Composition, Gating, Models

The 16 review subagent prompts live in dotagents `agents/`. Local installs expose them through `.agents/agents/` and Cursor `~/.cursor/agents/*.md` symlinks; fleet consumers receive the same prompts at `.agents/agents/`. `/review-fix-push` step 6 dispatches this fleet in parallel. Every agent uses `model: inherit` in frontmatter (same model as the orchestrator session).

---

## Always-run (12 agents)

These fire on every fan-out invocation.

| Agent | Lens | Bash? |
| --- | --- | --- |
| `guidelines-auditor` | Project conventions from AGENTS.md and linked rules | no |
| `guidelines-auditor` (2nd invocation) | Same — duplicate-invocation reduces false negatives per Anthropic's plugin pattern | no |
| `bug-scanner` | Logic errors, broken contracts, race conditions, edge cases | yes |
| `security-scanner` | Injection, XSS, auth bypass, CSRF, SSRF, crypto misuse, insecure defaults | yes |
| `secrets-scanner` | Hardcoded API keys, tokens, private keys, .env leaks | yes |
| `adversarial-reviewer` | Strategic pushback — is this the right solution at all? | yes |
| `simplification-reviewer` | Tactical — could this exact code be simpler? | no |
| `dependency-scanner` | New deps exist on registry; slopsquat defense | yes |
| `runtime-prober` | Crafted edge inputs against pure-ish functions in a sandboxed temp dir | yes |
| `history-reviewer` | `git log`/`git blame` for regressions and contradictions | yes |
| `test-reviewer` | Test quality, coverage gaps, realistic data, scenario framing | no |
| `error-handling-reviewer` | Silent failures, missing logging, swallowed exceptions | no |
| `docs-reviewer` | Inline comments and docs vs code | no |
| `db-migration-reviewer` | Destructive migrations, RLS, missing indexes, breaking column changes | yes |
| `infra-reviewer` | IAM sprawl, over-permissioned policies, missing deploy steps | yes |

**`db-migration-reviewer` and `infra-reviewer` are always-run** even though their lenses are scoped — directory-based gates are fragile (different projects use different conventions), and the cost of running an agent that exits with the empty-scope verdict is ~50 tokens. Wall-clock cost is parallel anyway.

The empty-scope verdict pattern: agents whose lens doesn't apply to the current diff return:

```text
**Ready to ship: Yes**
**Reasoning:** No <files in lens> in scope.
```

## Extension-gated (1 agent)

Fires only when `git diff --name-only origin/main...HEAD` matches the gate.

| Agent | Gate |
| --- | --- |
| `a11y-reviewer` | `**/*.{tsx,jsx,vue,astro,html}` |

`.css` is **not** in the gate — Tailwind config tweaks and color-token renames produce noise without surfacing real WCAG issues. The remaining a11y signals (color contrast in inline styles, focus management, semantic HTML) live in markup-bearing files.

## Per-finding adjudication (1 agent)

Not part of the fan-out. Invoked once per surviving Critical/Important finding by step 7.

| Agent | Lens |
| --- | --- |
| `confidence-scorer` | Severity adjudication: Confirm Critical / Downgrade / False positive |

`confidence-scorer` is exempt from the standard contract (severity buckets, finding cap, verdict line). It returns a 2-field block: `Adjudication` + `Justification`.

## Why duplicate `guidelines-auditor`

Anthropic's plugin pattern duplicates a critical specialist to reduce false negatives. Two independent passes through the same lens produce overlapping but non-identical findings. The orchestrator dedupes by `(file, line, issue)` at step 7. Cost is two parallel Task calls; benefit is meaningful coverage gain on guideline violations specifically.

## Model: inherit

All agents set `model: inherit` in frontmatter so each subagent uses the same model as the `/review-fix-push` orchestrator session. Pick the parent model for the review (e.g. a strong reasoning model for a large diff); subagents follow automatically. Final synthesis at step 8 still happens in the orchestrator's context.

## Token economics

Per the artifact: agents use ~4× tokens of chat; multi-agent systems ~15× chat. This is justified for high-value tasks (research, comprehensive PR review, audits) but not for trivial single-file changes. SKILL.md's "for small changes (a few files), review inline — no agents needed" rule handles this — fan-out kicks in for diffs with multiple files or non-trivial logic.
