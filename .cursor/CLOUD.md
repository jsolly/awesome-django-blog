# Cursor Cloud Agent notes

This file is read by Cloud / Background Agents only (local IDE chat ignores it).
Repo `AGENTS.md` still applies first; this file overlays cloud-specific facts.

## Skills

Public fleet skills are installed at `~/.cursor/skills` by `.cursor/install-cloud-skills.sh`
(via `.cursor/environment.json` `install`). Source: <https://github.com/jsolly/agent-skills>
(sanitized public mirror — not private `dotagents`).

There is **no** `~/code/dotagents` on this VM. Do not look for it or claim child repos inherit it.

If slash-skill autocomplete is empty on a follow-up turn, invoke the skill by name in prose
(known Agents Window bug; typed invoke still works).

Private laptop-only skills (e.g. `verify-ui`) are **not** available here. Follow this repo's
`AGENTS.md` Local UI verification stanza for UI smoke instead of inventing `/verify-ui`.

## Hooks / guards

User-level `~/.cursor/hooks.json` from a laptop does **not** run in cloud. Only hooks committed
under this repo's `.cursor/hooks.json` (or team/enterprise hooks) apply.
