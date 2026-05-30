# Agent safety rules — block `git push/commit --no-verify`

These guards make "never bypass hooks with `--no-verify`" **mechanical**, not advisory. Each agent has its own enforcement layer; there is no shared git wrapper.

## Two layers

| Layer | Where | Covers |
| --- | --- | --- |
| **Home** | `~/.claude`, `~/.cursor`, `~/.codex` via install script | All repos on that machine (Claude, Cursor IDE/CLI, Codex) |
| **Repo** | `.agents/hooks/block-git-no-verify.sh` + merged `.cursor/hooks.json` | Cursor Cloud and defense-in-depth locally |

**Home layer** — run once per machine:

```bash
.agents/scripts/install-agent-git-guards.sh
```

**Repo layer** — ships in fleet subtree; merge into each app repo:

```bash
bash .agents/scripts/merge-cursor-git-guard.sh
```

Roll out to all local fleet repos after subtree pull:

```bash
.agents/scripts/rollout-git-guards-to-repos.sh
```

Canonical snippets and the shared hook script live under `.agents/hooks/` (dotagents repo root; not all snippets ship in fleet).

---

## Propagation checklist

| Surface | Install path | Verify |
| --- | --- | --- |
| Home Mac | `.agents/scripts/install-agent-git-guards.sh` | jq checks below |
| Work Mac | setup-work-computer §2 (copy hooks) + §11 install | same jq checks |
| App repo (local + cloud) | subtree pull + `merge-cursor-git-guard.sh` | `jq '.hooks.beforeShellExecution' .cursor/hooks.json` |
| Codex | home install + `/hooks` trust once | hook listed in Codex `/hooks` |

---

## Shared hook script

`.agents/hooks/block-git-no-verify.sh` (fleet: `.agents/hooks/block-git-no-verify.sh`) parses the shell command (including compound commands split on `&&`, `||`, `;`, `|`) and blocks when a segment is `git push` or `git commit` with `--no-verify`.

---

## Claude Code

**Layers:** `permissions.deny` + `PreToolUse` hook on `Bash`.

Snippets:

- `hooks/claude-permissions-snippet.json` — deny rules
- `hooks/claude-hooks-snippet.json` — adds the Bash hook under `PreToolUse`

Deny rules (also in snippet):

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

The `PreToolUse` hook is belt-and-suspenders when `defaultMode` is `bypassPermissions` — exit code `2` blocks before the shell runs.

**Verify:**

```bash
jq '.permissions.deny, .hooks.PreToolUse' ~/.claude/settings.json
```

In Claude Code: `/permissions` should list the deny entries; `/hooks` reloads after edits.

**Caveat:** Bash permission patterns are fragile (aliases, env-var splicing, `-f` short flags). The hook catches full command strings more reliably than deny patterns alone.

---

## Cursor (IDE agent)

**Home layer:** `beforeShellExecution` hook in `~/.cursor/hooks.json` (snippet: `hooks/cursor-hooks-snippet.json`).

**Repo layer:** merged entry in `.cursor/hooks.json` calling `bash .agents/hooks/block-git-no-verify.sh` (via `merge-cursor-git-guard.sh`).

Home install symlinks the script at `~/.cursor/hooks/block-git-no-verify.sh` (paths in user `hooks.json` are relative to `~/.cursor/`).

Uses `failClosed: true` so a crashed hook denies instead of fail-open.

**Verify:** Cursor **Settings → Hooks**, or the **Hooks** output channel after triggering a blocked command.

---

## Cursor CLI (`cursor-agent`)

**Layer:** `permissions.deny` tokens in `~/.cursor/cli-config.json`.

Snippet: `hooks/cursor-cli-permissions-snippet.json`

```json
{
  "permissions": {
    "deny": [
      "Shell(git:push*--no-verify*)",
      "Shell(git:commit*--no-verify*)"
    ]
  }
}
```

Uses the `Shell(command:args)` form so `--no-verify` can appear anywhere in the args after `push`/`commit`.

**Verify:**

```bash
jq '.permissions.deny' ~/.cursor/cli-config.json
```

Deny wins over allow rules.

---

## Codex

**Layer:** `PreToolUse` hook on `Bash` in `~/.codex/hooks.json`.

Snippet: `hooks/codex-hooks-snippet.json` → installed to `~/.codex/hooks.json`.

Hooks are enabled by default. Non-managed hooks require trust review — open `/hooks` in Codex after install (one-time manual step).

**Verify:**

```bash
jq '.hooks.PreToolUse' ~/.codex/hooks.json
```

Prefix rules in `~/.codex/rules/*.rules` are **not** used here; they only match command prefixes and miss `git push origin main --no-verify`. The hook handles trailing flags.

---

## Precedence notes (Claude)

Per [Claude Code permissions docs](https://code.claude.com/docs/en/permissions): deny → ask → allow; deny rules from any scope win. PreToolUse hooks that exit `2` block before permission rules run (stronger than allow, complementary to deny).

---

## What this does NOT do

- Does not block `--no-verify` when git is invoked outside these agents (manual terminal, CI, other tools).
- Does not block force-push via `-f` short flag in Claude deny patterns (documented fragility).
- Does not replace fixing broken pre-commit/pre-push hooks — it only stops agents from bypassing them.
