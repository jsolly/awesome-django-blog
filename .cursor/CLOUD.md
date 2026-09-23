# Cursor Cloud Agent notes

This file is read by Cloud / Background Agents only (local IDE chat ignores it).
Repo `AGENTS.md` still applies first; this file overlays cloud-specific facts.

## Skills package (private checkout)

`.cursor/install-cloud-skills.sh` (via `.cursor/environment.json` `install`) copies
**skills, agents, cited rules, the connector catalog, and `gate/gate-lib.sh`** from a
private `dotagents` checkout into VM home paths. Preferred source is a host-local
tree (`DOTAGENTS_ROOT`, or this repo when the installer is running from it). If
none is present it fetches `jsolly/dotagents` in this order: `gh api` tarball,
`gh repo clone`, then `git clone`. GitHub MCP read access is **not** git clone
credentials — a child-repo VM often needs `gh` (or `repositoryDependencies`)
before anonymous HTTPS clone works. There is no public skills mirror.

| Artifact | VM path | Notes |
| --- | --- | --- |
| Skills | `~/.cursor/skills/` | Same discovery as laptop `~/.cursor/skills` |
| Agents | `~/.cursor/agents/` | One `.md` file per reviewer/scanner agent |
| Cited rules | `~/.cursor/dotagents-package/rules/` | **Read from here** when a skill cites `rules/<name>.md` |
| Connector catalog | `~/.cursor/dotagents-package/mcps/catalog.json` | The cloud-first canon for MCP servers + marketplace plugins. `/optimize-workspaces` reconciles the live session against it — no laptop checkout needed |
| Pre-commit gate lib | `~/.cursor/dotagents-package/gate/gate-lib.sh` | Canonical copy. Export `DOTAGENTS_GATE_LIB` to this path. Child `.git-hooks/pre-commit` shims source `${DOTAGENTS_GATE_LIB:-$HOME/code/dotagents/gate/gate-lib.sh}` |

### Agents / Review Task fallback

`~/.cursor/agents/` is installed on Cloud, but Task `subagent_type` names are
laptop/IDE-oriented and often unavailable here. Cloud `/ship` uses
`general-purpose` Tasks that each read `~/.cursor/agents/<name>.md` and follow
that lens plus `skills/ship/references/output-contract.md`. Same roster names
and depth gates as `skills/ship/references/review-roster.md` — do not invent
parallel lenses.

Laptop-only skills (see `skills/laptop-only.txt`) are **not** installed on cloud.

There is **no** full `~/code/dotagents` checkout on this VM unless the current
repo *is* dotagents. The installer may plant a **stub symlink** at
`~/code/dotagents/gate/gate-lib.sh` so child pre-commits' default source path
resolves when `DOTAGENTS_GATE_LIB` is unset (non-login `bash -c` / git hooks).
The installer does **not** replace `gate-lib.sh` inside a real `~/code/dotagents`
checkout. That stub is **not** a laptop tree — do not look for skills there, do not claim
child repos inherit home wiring, and do **not** hand-copy `gate-lib.sh` into
this repo. Do **not** vendor the private dotagents tree into this repo.

`.cursor/environment.json` sets `repositoryDependencies` to
`github.com/jsolly/dotagents` so the generated GitHub token can include that
private repo (it does **not** auto-clone). The Cursor GitHub App must allowlist
`jsolly/dotagents`. `install` / `start` also export `DOTAGENTS_GATE_LIB` to the
canonical package path.

`~/.cursor/rules` from a laptop home is **not** auto-applied on cloud. User Rules + repo
`AGENTS.md` + this file carry policy; skills that cite rules must read the copies under
`~/.cursor/dotagents-package/rules/`.

## Connectors and marketplace plugins

The account's marketplace plugins follow you onto this VM; `~/.cursor/mcp.json` does **not**. The
canon is `mcps/catalog.json` (copied to `~/.cursor/dotagents-package/mcps/`): it records every
fleet-worthy connector with its plugin id / remote URL, the surfaces it belongs on, and its rule.
Run `/optimize-workspaces` to reconcile this session against it. Two standing rules: GitHub MCP access
may use the approved marketplace plugin `48677658`, the `github-local` account connector, or `gh` — with the same authorization rules — and
a connector that crosses repos gets its catalog row in the **same change** that adds it.

## Durable planning and human handoffs

When this harness lacks a usable native planning mode, load
`~/.cursor/skills/persist-todos-in-todoist/SKILL.md` for durable Todoist outcomes,
cooperative claims and human handoffs. Human actions and ad hoc work outside a
repo also use that skill. A supported native repo plan needs no Todoist mirror;
reconsider this integration when Cursor Cloud or Grok Bot gains native planning.
Reconcile already-tracked commitments regardless of the current harness.

For Todoist-backed work, load the expected John user ID and email from the
installed private persistence skill. Require both user-info fields to match
before queue pickup or writes; missing private identity policy or an account
mismatch stops Todoist work and is reported. Then read a known shared task and
all its comments;
shared-task visibility alone is not identity proof. Discover only work in this repo or assigned
role, inside existing authorization. Missing tracker access blocks unattended
Todoist pickup; explicitly requested read-only analysis may continue with an
honest unsynced status. Native repo plans without a Todoist obligation do not
require the connector. Catalog installation is not authentication proof.

## Laptop-only (not on cloud)

- `setup/install-local-agent-runtime.sh` and `setup/doctor-agents.sh`
- User-level `~/.cursor/hooks.json` and other home hooks/guards
- Laptop-only skills (e.g. `setup-personal-machine`, `solly-create-skill`)

## Skills / slash commands

If slash-skill autocomplete is empty on a **follow-up** turn, invoke the skill by name in prose
(known Agents Window bug; typed invoke still works).

`/verify-ui` ships in this package — use it for UI smoke when the skill is present. If it is
missing, follow this repo's `AGENTS.md` **Local UI verification** stanza instead.

Product UI must not load runtime CSS/JS from third-party CDNs (jsDelivr, unpkg, cdnjs, esm.sh,
Google Fonts CSS, and similar). Prefer npm/local packages and first-party origins. Canon: laptop
global brief **No CDN for app assets**; also this repo's `AGENTS.md` when present.

Vercel Git repos must not auto-Preview every branch. Production stays on `main`; opt-in `/preview`
only when John asks. Canon: laptop global brief **No automatic Vercel Previews**; also this repo's
`AGENTS.md` when present.

Personal AWS/SAM Lambdas keep the full enrichment path (copied logger, both alarms, error-level
metric filter, `AlertTopicArn`). Copy retention and thresholds; never invent. Missing `~/code/shared-infra` is `not done`. Canon: laptop global brief **Shared-infra Lambdas**; also
this repo's `AGENTS.md` when present. Add or repair via `/new-solly-repo`.

`/remove-feature` ships in this package — load it before substantial code deletion (a feature,
module, many files, a large deleted-line diff), not only when the user types the slash command.
Tiny unused-line deletes and complexity-only cleanup (`/remove-slop`) stay ordinary editing.

## Outbound identity (standing rule, not a skill)

Outbound is the assistant, not John. Write in the assistant voice about John — never first person
as John, never signed with his name alone. The last line is a hyphen signature line (hyphen, space,
John's AI Assistant), never a markdown list. Never Holiday Proton. Communications addressed to
third-party people or organizations hold 15 minutes unless John says send now; internal messages
and own-repo or operational work have no hold. A held message waits as the full draft in the chat
plus a one-shot timed send where the host has one; channel Drafts (Fastmail `draft_email`) are a
last resort, never the default. There is no outbound skill to load (the former one is retired) — read
`~/.cursor/dotagents-package/rules/outbound-identity.md` for the hold-surface order and the receipt
before claiming `done`, `holding`, or `sent`.

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
