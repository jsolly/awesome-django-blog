# Agent safety rules — block `git push/commit --no-verify`

"Never bypass hooks with `--no-verify`" is **mechanical**, not advisory. A repo-level Cursor hook enforces it for both the IDE agent and Cursor Cloud — the runtime for fleet repos. (There is no home-machine / multi-provider install anymore; everything runs in Cursor containers/cloud.)

## The guard

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
