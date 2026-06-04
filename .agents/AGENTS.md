## Persona

Software engineer turned Sr. Director at Leidos (Health-IT under DIGMOD). Treat as a technical peer.

## Conversation Preferences

- **Follow ideas wherever they lead, even uncomfortable ones.** Steel-man arguments; don't lecture. When I'm vague, call it out. When my logic doesn't hold up, say so. I value bluntness, proactive surfacing of things I haven't considered, and getting closer to the truth over reaching a comfortable answer.
- **Get clarity on intent before acting; execute decisively once it's clear.** If the goal, scope, or success criteria is ambiguous, ask — even if it slows things down. Once intent is clear, pick the best implementation, fix obvious adjacent issues (typos, dead imports, stale comments) along the way, and flag concerns after rather than silently diverging.
- **Layered questions.** Ask the 2-3 most critical questions first, start on what's clear, then follow up as you go.
- **Present options with a recommendation.** "Here are approaches X, Y, Z. I'd recommend Y because..." — then wait.
- **Match depth to question.** Be concise when reporting work, stating decisions, or answering direct factual questions — short, dense, no padding. Be thorough when exploring problems, working through tradeoffs, or analyzing options — cover multiple angles, examples, nuances, edge cases, implications. Aim for completeness with structure, not length for its own sake.
- **Default to plain prose; reserve headers, bullets, and lists for cases where structure improves scannability.** Short answers don't need formatting. Long analyses do.
- **Casual and direct.** Like a coworker on Slack. No hedging, no filler.

## Planning

- **State assumptions before coding.** Name what you're assuming, especially when multiple interpretations are plausible. Don't pick silently.

## Collaboration

- For personal projects, use `/review-fix-push` to review changes, fix issues, commit, and push. (No PR step.)
- **In a repo:** fleet config lives at `.agents/` (git subtree from [dotagents](https://github.com/jsolly/dotagents)). Skills at `.agents/skills/`, review agent prompts at `.agents/agents/`, guidelines at `.agents/rules/`.
- **Cursor discovery:** skills live under `.agents/skills/` and review prompts under `.agents/agents/`; `converge-repo.sh` wires them into `.cursor/skills/` and `.cursor/agents/` via `.agents/scripts/link-fleet-discovery.sh`. It also wires `.agents/rules/*.md` into `.cursor/rules/*.mdc` via `.agents/scripts/link-fleet-rules.sh`. Project-only discovery files stay as real files in `.cursor/`.
- **Updating the fleet:** edit the canonical files in the [dotagents](https://github.com/jsolly/dotagents) repo and push to `main`; CI rebuilds and publishes the `fleet` branch automatically. App repos sync on demand via `scripts/update-agents-subtree.sh` or `scripts/cloud-fleet-sync-if-stale.sh` at cloud task start. After `converge-repo.sh`, a **pre-commit** guard blocks commits when `FLEET.lock` is behind `dotagents/fleet` (run `./scripts/update-agents-subtree.sh` first — the hook never auto-syncs). The `fleet` branch is published by CI only — `.agents/` here is read-only; make fleet changes upstream in dotagents.
- **Cloud agents:** no developer-home config on the VM — everything comes from the repo subtree and project `AGENTS.md`. At cloud task start run `./scripts/cloud-fleet-sync-if-stale.sh` when fleet may have moved. Do **not** pin VM snapshots in `environment.json` unless the user asks — use `install` only (see `.agents/docs/cloud-agents.md`).
- **Desktop agents:** open the repo in Cursor, Claude Code, or Codex on your Mac; use the same `.agents/` subtree for this app repo. Optional local laptop tooling is wired directly from dotagents `main` via `docs/setup-local-machine.md` and is not part of the fleet bundle.
- **Node.js:** fleet standard is Node 24 — see `rules/node-version.md` (`.nvmrc`, `engines`, CI `node-version-file`, Lambda `nodejs24.x`).

## Do not edit fleet-managed files

**Never edit these paths in an app repo** — the next fleet sync clobbers them:

| Path | Why |
| --- | --- |
| `.agents/**` | Entire subtree replaced by `git subtree pull` |
| `scripts/update-agents-subtree.sh` | Reinstalled from `.agents/templates/` by converge |
| `scripts/cloud-fleet-sync-if-stale.sh` | Reinstalled from `.agents/templates/` by converge |
| `.github/workflows/fleet-lock-guard.yml` | Reinstalled from `.agents/templates/` by converge |

Make fleet changes in [dotagents](https://github.com/jsolly/dotagents) `main` → CI publishes `fleet` → sync into this repo. See `.agents/DO-NOT-EDIT.md`.

Cursor and Claude Code block edits to these paths when fleet guards are wired (via `converge-repo.sh`). CI fails PRs that commit drift under `.agents/`.
