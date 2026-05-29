# Agent Fleet — Composition, Gating, Models

The 16 review subagents in `.agents/agents/` are dispatched in parallel by `/review-fix-push` step 6. This file documents which agents fire when, why, and on what model.

---

## Always-run (12 agents)

These fire on every fan-out invocation.

| Agent | Lens | Model | Bash? |
| --- | --- | --- | --- |
| `guidelines-auditor` | Project conventions from AGENTS.md and linked rules | sonnet | no |
| `guidelines-auditor` (2nd invocation) | Same — duplicate-invocation reduces false negatives per Anthropic's plugin pattern | sonnet | no |
| `bug-scanner` | Logic errors, broken contracts, race conditions, edge cases | sonnet | yes |
| `security-scanner` | Injection, XSS, auth bypass, CSRF, SSRF, crypto misuse, insecure defaults | **opus** | yes |
| `secrets-scanner` | Hardcoded API keys, tokens, private keys, .env leaks | haiku | yes |
| `adversarial-reviewer` | Strategic pushback — is this the right solution at all? | **opus** | yes |
| `simplification-reviewer` | Tactical — could this exact code be simpler? | sonnet | no |
| `dependency-scanner` | New deps exist on registry; slopsquat defense | haiku | yes |
| `runtime-prober` | Crafted edge inputs against pure-ish functions in a sandboxed temp dir | sonnet | yes |
| `history-reviewer` | `git log`/`git blame` for regressions and contradictions | sonnet | yes |
| `test-reviewer` | Test quality, coverage gaps, realistic data, scenario framing | sonnet | no |
| `error-handling-reviewer` | Silent failures, missing logging, swallowed exceptions | sonnet | no |
| `docs-reviewer` | Inline comments and docs vs code | haiku | no |
| `db-migration-reviewer` | Destructive migrations, RLS, missing indexes, breaking column changes | sonnet | yes |
| `infra-reviewer` | IAM sprawl, over-permissioned policies, missing deploy steps | sonnet | yes |

**`db-migration-reviewer` and `infra-reviewer` are always-run** even though their lenses are scoped — directory-based gates are fragile (different projects use different conventions), and the cost of running an agent that exits with the empty-scope verdict is ~50 tokens. Wall-clock cost is parallel anyway.

The empty-scope verdict pattern: agents whose lens doesn't apply to the current diff return:

```text
**Ready to ship: Yes**
**Reasoning:** No <files in lens> in scope.
```

## Extension-gated (1 agent)

Fires only when `git diff --name-only origin/main...HEAD` matches the gate.

| Agent | Gate | Model |
| --- | --- | --- |
| `a11y-reviewer` | `**/*.{tsx,jsx,vue,astro,html}` | haiku |

`.css` is **not** in the gate — Tailwind config tweaks and color-token renames produce noise without surfacing real WCAG issues. The remaining a11y signals (color contrast in inline styles, focus management, semantic HTML) live in markup-bearing files.

## Per-finding adjudication (1 agent)

Not part of the fan-out. Invoked once per surviving Critical/Important finding by step 7.

| Agent | Lens | Model |
| --- | --- | --- |
| `confidence-scorer` | Severity adjudication: Confirm Critical / Downgrade / False positive | haiku |

`confidence-scorer` is exempt from the standard contract (severity buckets, finding cap, verdict line). It returns a 2-field block: `Adjudication` + `Justification`.

## Why duplicate `guidelines-auditor`

Anthropic's plugin pattern duplicates a critical specialist to reduce false negatives. Two independent passes through the same lens produce overlapping but non-identical findings. The orchestrator dedupes by `(file, line, issue)` at step 7. Cost is two parallel Task calls; benefit is meaningful coverage gain on guideline violations specifically.

## Why these models

The artifact's recommendation (paraphrased): use Haiku for narrow scans (linter, deps, pattern matching), Sonnet for reasoning-heavy lenses, Opus for catastrophic-failure-mode lenses where false negatives are most expensive.

Mapping to our fleet:

- **Opus (2 agents)**: `security-scanner` (tainted-data-flow analysis is multi-step inference; the sole-gate workflow makes a missed CVE catastrophic), `adversarial-reviewer` (cross-file pattern matching + architectural judgment).
- **Sonnet (9 agents)**: mid-complexity reasoning lenses where sonnet is the cost/quality sweet spot.
- **Haiku (5 agents)**: `dependency-scanner` (registry lookups), `secrets-scanner` (pattern matching), `docs-reviewer` (comment-vs-code matching), `a11y-reviewer` (static lint-like checks), `confidence-scorer` (single-finding adjudication with rubric).
- **Orchestrator**: the user's main session, typically Opus 4.7 with 1M context. Final synthesis at step 8 happens in the orchestrator's context.

The 2-opus promotion targets the agents where false negatives are most expensive: a missed security finding ships an exploit; a missed architectural concern ships a load-bearing mistake into the codebase.

## Token economics

Per the artifact: agents use ~4× tokens of chat; multi-agent systems ~15× chat. This is justified for high-value tasks (research, comprehensive PR review, audits) but not for trivial single-file changes. SKILL.md's "for small changes (a few files), review inline — no agents needed" rule handles this — fan-out kicks in for diffs with multiple files or non-trivial logic.
