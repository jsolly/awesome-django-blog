# Cursor Cloud Agent notes

This file is read by Cloud / Background Agents only (local IDE chat ignores it).
Repo `AGENTS.md` still applies first; this file overlays cloud-specific facts.

## Public agent-skills package (mirror)

`.cursor/install-cloud-skills.sh` (via `.cursor/environment.json` `install`) shallow-clones
<https://github.com/jsolly/agent-skills> and installs the **full published package**:

| Artifact | VM path | Notes |
| --- | --- | --- |
| Skills | `~/.cursor/skills/` | Same discovery as laptop `~/.cursor/skills` |
| Agents | `~/.cursor/agents/` | One `.md` file per reviewer/scanner agent |
| Cited rules | `~/.cursor/agent-skills-package/rules/` | **Read from here** when a skill cites `rules/<name>.md` |

Source is the sanitized public mirror — **not** private `~/code/dotagents`.

There is **no** `~/code/dotagents` on this VM. Do not look for it or claim child repos inherit it.
Do **not** vendor the private dotagents tree into this repo.

`~/.cursor/rules` from a laptop home is **not** auto-applied on cloud. User Rules + repo
`AGENTS.md` + this file carry policy; skills that cite rules must read the copies under
`~/.cursor/agent-skills-package/rules/`.

## Laptop-only (not on cloud)

- `scripts/install-local-agent-runtime.sh` and `scripts/doctor-agents.sh`
- User-level `~/.cursor/hooks.json` and other home hooks/guards
- Private skills (e.g. `verify-ui`, `publish-skills`, family-memory)

## Skills / slash commands

If slash-skill autocomplete is empty on a **follow-up** turn, invoke the skill by name in prose
(known Agents Window bug; typed invoke still works).

Private laptop-only skills are **not** available here. For UI smoke, follow this repo's
`AGENTS.md` **Local UI verification** stanza — do not invent `/verify-ui` when that skill is absent.

## Hooks / guards

Only hooks committed under this repo's `.cursor/hooks.json` (or team/enterprise hooks) apply.
User-level hook config from a laptop does not run in cloud.

## AWS reads (same role as the laptop)

`.cursor/aws-oidc-login.sh` runs on `install` **and** `start`. It writes
`~/.aws/config` with `credential_process` (no static STS keys — those expire in
1h and Builds do not re-run `install`). Each `aws` call mints a Cursor OIDC JWT
(`aud: sts.amazonaws.com`) and assumes `arn:aws:iam::730335616323:role/agent-readonly`.
That is the **same** IAM role laptop agents use via Identity Center `AgentReadOnly` —
`ReadOnlyAccess` plus the deny-secrets overlay. Do not look for `fleet-deploy` or
`agent-deploy`; those laptop deploy identities are gone.

After install, `AWS_PROFILE=agent-readonly` is set. Use it for CloudWatch / Lambda
describe/get/list. `ssm:GetParameter*` and Secrets Manager gets are explicit deny.
Do **not** invoke `*-live-provider-check` — that grant is CI and human-admin only.

Allow `sts.amazonaws.com` (and regional STS if used) on this environment's network
policy or assume-role will hang. The role ARN may be a Cursor Environment Variable
(`AWS_ROLE_ARN`); it is not a secret. Never store long-lived AWS keys.

Claude/Codex cloud OIDC is stubbed until those vendors publish an issuer; then add
another IAM OIDC provider + trust statement on the **same** `agent-readonly` role.
