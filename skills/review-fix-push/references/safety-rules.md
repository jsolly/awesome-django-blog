# Agent safety rules — block `git push/commit --no-verify`

"Never bypass hooks with `--no-verify`" is **mechanical**, not advisory. Two enforcement layers:

| Layer | Where | Covers |
| --- | --- | --- |
| **Repo** | `.agents/hooks/block-git-no-verify.sh` merged into `.cursor/hooks.json` | Cursor IDE and Cursor Cloud in that repo |
| **Home (desktop)** | `~/.claude/settings.json`, `~/.cursor/hooks.json`, `~/.codex/hooks.json` via `block-git-no-verify.sh` | All repos on that Mac for those tools |

Install desktop guards and sound hooks from dotagents: `bash ~/code/dotagents/scripts/install-desktop-agent-hooks.sh` (sounds only) plus existing Claude/Codex Bash `PreToolUse` wiring for the git guard. Fleet repos get the repo layer from `converge-repo.sh` automatically.

## The repo guard

The hook ships in the fleet subtree and is wired into the repo's `.cursor/hooks.json`:

```bash
bash .agents/scripts/merge-cursor-git-guard.sh
```

This runs automatically during fleet sync and onboarding (`.agents/scripts/converge-repo.sh` calls it), so a converged repo already has it. The merge adds a `beforeShellExecution` hook with `failClosed: true` (a crashed hook denies rather than fail-open) that calls:

```bash
bash .agents/hooks/block-git-no-verify.sh
```

`block-git-no-verify.sh` parses the shell command — including compound commands split on `&&`, `||`, `;`, `|` — and blocks when any segment is `git push` or `git commit` with `--no-verify`.

## Verify

```bash
jq '.hooks.beforeShellExecution' .cursor/hooks.json
```

Cursor surfaces a blocked command in **Settings → Hooks** and the **Hooks** output channel.

## What this does NOT do

- Does not block `--no-verify` when git is invoked outside the Cursor agent (manual terminal, CI, other tools).
- Does not replace fixing broken pre-commit/pre-push hooks — it only stops the agent from bypassing them.
