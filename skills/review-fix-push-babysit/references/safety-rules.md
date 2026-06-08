# Agent safety rules — block `git push/commit --no-verify`

"Never bypass hooks with `--no-verify`" is **mechanical**, not advisory. Two enforcement layers:

| Layer | Where | Covers |
| --- | --- | --- |
| **Repo** | `.agents/hooks/block-git-no-verify.sh` merged into repo `.cursor/hooks.json` by `converge-repo.sh` | Cursor IDE and Cursor Cloud in that repo |
| **Home (desktop)** | `~/code/dotagents/hooks/block-git-no-verify.sh` merged into `~/.cursor/hooks.json`, `~/.claude/settings.json`, and `~/.codex/hooks.json` by `scripts/install-local-agent-runtime.sh` | Local Cursor, Claude Code, and Codex sessions, including dotagents itself and repos before fleet convergence |

Install or refresh the local desktop guards with:

```bash
bash ~/code/dotagents/scripts/install-local-agent-runtime.sh personal
# or
bash ~/code/dotagents/scripts/install-local-agent-runtime.sh work
```

Fleet repos get the repo layer from `converge-repo.sh` automatically. Desktop sound hooks are separate and optional: `bash ~/code/dotagents/scripts/install-desktop-agent-hooks.sh`.

## The repo guard

The hook ships in the fleet subtree and is wired into the repo's `.cursor/hooks.json`:

```bash
bash .agents/scripts/merge-cursor-hooks.sh
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

## The local desktop guard

The local runtime installer preserves existing hook entries and adds exactly one guard command per tool:

```bash
bash ~/code/dotagents/hooks/block-git-no-verify.sh
```

Cursor uses `beforeShellExecution`; Claude Code and Codex use `PreToolUse` for Bash. This protects local sessions even in repos that are not fleet-converged. App repos should still rely on the repo guard as the cloud-compatible source of enforcement.

## What this does NOT do

- Does not block `--no-verify` when git is invoked outside configured agent hooks (manual terminal, CI, other tools).
- Does not replace fixing broken pre-commit/pre-push hooks — it only stops the agent from bypassing them.
