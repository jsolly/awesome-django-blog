# Cursor Cloud Agent notes

This file is read by Cloud / Background Agents only (local IDE chat ignores it).
Repo `AGENTS.md` still applies first; this file overlays cloud-specific facts.

## Skills package (private checkout)

`.cursor/install-cloud-skills.sh` (via `.cursor/environment.json` `install`) copies
**skills, agents, and cited rules** from a private `dotagents` checkout into VM
home paths. Preferred source is a host-local tree (`DOTAGENTS_ROOT`, or this
repo when the installer is running from it). If none is present it may shallow-
clone `jsolly/dotagents`. There is no public skills mirror.

| Artifact | VM path | Notes |
| --- | --- | --- |
| Skills | `~/.cursor/skills/` | Same discovery as laptop `~/.cursor/skills` |
| Agents | `~/.cursor/agents/` | One `.md` file per reviewer/scanner agent |
| Cited rules | `~/.cursor/dotagents-package/rules/` | **Read from here** when a skill cites `rules/<name>.md` |

Laptop-only skills (see `skills/laptop-only.txt`) are **not** installed on cloud.

There is **no** `~/code/dotagents` on this VM unless the current repo *is*
dotagents. Do not look for a laptop home wiring path or claim child repos inherit
it. Do **not** vendor the private dotagents tree into this repo.

`~/.cursor/rules` from a laptop home is **not** auto-applied on cloud. User Rules + repo
`AGENTS.md` + this file carry policy; skills that cite rules must read the copies under
`~/.cursor/dotagents-package/rules/`.

## Laptop-only (not on cloud)

- `setup/install-local-agent-runtime.sh` and `setup/doctor-agents.sh`
- User-level `~/.cursor/hooks.json` and other home hooks/guards
- Laptop-only skills (e.g. `setup-personal-machine`, `create-lambda`)

## Skills / slash commands

If slash-skill autocomplete is empty on a **follow-up** turn, invoke the skill by name in prose
(known Agents Window bug; typed invoke still works).

`/verify-ui` ships in this package — use it for UI smoke when the skill is present. If it is
missing, follow this repo's `AGENTS.md` **Local UI verification** stanza instead.

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
