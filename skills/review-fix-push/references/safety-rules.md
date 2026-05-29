# Safety Rules — `permissions.deny` in `~/.claude/settings.json`

The skill states "Never use `--no-verify`" and "Never `git push --force`" as instructions to the model. These deny rules make those instructions **mechanical**, not advisory: any tool call matching them is rejected by Claude Code before reaching the shell, regardless of what the model intends.

This file documents the rules; they live in `~/.claude/settings.json` because that's where Claude Code reads `permissions.deny`. The connection to `/review-fix-push` is conceptual — these are safety nets for the skill's "no PR, push directly to main" model.

---

## The rules

```json
{
  "permissions": {
    "deny": [
      "Bash(git push *--force*)",
      "Bash(git push *--force-with-lease*)",
      "Bash(git push *--no-verify*)",
      "Bash(git commit *--no-verify*)",
      "Bash(git reset --hard*)"
    ]
  }
}
```

## What each rule blocks

| Rule | Blocks | Why |
| --- | --- | --- |
| `Bash(git push *--force*)` | `git push --force`, `git push origin --force`, `git push --force HEAD:main`, etc. | Force-pushes overwrite remote main; reviewer pushes have no business doing this. |
| `Bash(git push *--force-with-lease*)` | Same as above with `--force-with-lease` | Still rewrites history; safer than `--force` but not safe enough for a sole-gate workflow. |
| `Bash(git push *--no-verify*)` | `git push --no-verify HEAD:main`, etc. | Bypasses pre-push hooks the user trusts. The skill explicitly forbids this. |
| `Bash(git commit *--no-verify*)` | `git commit --no-verify -m "..."`, etc. | Bypasses pre-commit hooks. |
| `Bash(git reset --hard*)` | `git reset --hard`, `git reset --hard origin/main`, etc. | Loses uncommitted work; the skill's flow never needs this. |

## Caveat from the docs (fragility)

Per the [Claude Code permissions docs](https://code.claude.com/docs/en/permissions): "Bash permission patterns that try to constrain command arguments are fragile."

Variations that could evade these rules:

- **Aliases**: a shell alias mapping `gpf` to `git push --force` would route around the deny rule because the matcher sees `gpf`, not the expanded command.
- **Env-var splicing**: `FLAGS="--force" git push $FLAGS` — the matcher sees the literal command string before the shell expands `$FLAGS`. Whether the deny rule fires depends on Claude Code's invocation point.
- **Short flags for `--force`**: `-f` is intentionally not in the deny list because `Bash(git push *-f*)` would also match `--fast-forward` and similar legitimate flags. The skill instructs the model not to use `-f` either; this is belt-and-suspenders.
- **Compound commands**: per the docs, Claude Code splits compound commands by `&&`, `||`, `;`, `|`, etc., and checks each subcommand independently. So `git push --force && echo done` is correctly blocked. But complex shell constructions might evade.

For solo prototyping the threat model is "don't accidentally type `--force`," not "thwart adversarial injection." If the model is ever observed routing around a rule, expand the pattern set.

## Verifying the rules

After installing, confirm via:

```bash
# Check that the deny rules are present
jq '.permissions.deny' ~/.claude/settings.json

# In any Claude Code session, run /permissions and look for the deny entries
```

To test a deny rule without actually running the dangerous command, ask Claude Code in a sandbox session to attempt it — the call should be rejected before the shell sees it.

## Precedence (per the docs)

Rules are evaluated in order: **deny → ask → allow**. The first matching rule wins, so deny rules always take precedence over allow rules. Hooks (PreToolUse) cannot override deny rules — even a hook returning `permissionDecision: "allow"` is overruled by a matching deny.

This is what makes deny rules the right tool here: they're stronger than the model's intent and stronger than any other harness layer.

## What this file does NOT do

- **Does not enforce these rules** — the rules live in `~/.claude/settings.json`. This file just documents them.
- **Does not protect against `git` directly invoked outside Claude Code** — pre-commit hooks at the git layer (e.g., via the `pre-commit` framework, or a `.git/hooks/pre-push` script) are the defense for that. Out of scope here.
- **Does not block `git config alias.gpf "push --force"`** — alias creation is its own concern. A deny on `Bash(git config alias.* push*--force*)` could help; not currently in the rule set.
