# Per-Project Post-CI Deploys (Step 13)

Some projects require extra deploy steps after pushing because CI doesn't cover every path — e.g., SAM/CDK stacks, Terraform, Docker image pushes, Lambda code updates, manual cache invalidations.

This file documents the patterns; the actual rules per repo live in each project's `AGENTS.md`.

**Step 13 runs only after step 12 CI babysit succeeds (or CI is absent).** Do not run manual deploys when CI is red.

**Step 13 is mandatory when triggers match.** Do not end the skill with "remember to run SAM deploy" — run it (unless credentials are missing or the deploy is destructive and needs confirmation).

---

## How to detect which apply

In step 3 (load guidelines), capture post-push deploy rules into `{POST_PUSH_DEPLOYS}`. Examples:

- "SAM deploy required when `aws/template.yaml`, `aws/deploy.sh`, `src/handlers/`, or `src/lib/` changes — command `npm run deploy:aws`."
- "Run `terraform apply` from `infra/` after any `*.tf` change."
- "Lambda code-only updates to `src/handlers/` are deployed by the `Deploy Website` GitHub Actions workflow — no manual step."

The pattern is: **paths trigger commands**.

Also read `docs/deploy-gotchas.md` (or equivalent) for preconditions — e.g., merge to `main` before SAM deploy when Lambda env vars change.

## How to execute (step 13)

After the push succeeds (step 11) and CI is green (step 12):

1. Re-check `{POST_PUSH_DEPLOYS}` against committed files (`git diff --name-only origin/main~1 HEAD` or `origin/main...HEAD`).
2. If any rule's path trigger matches a committed file, **run the deploy command automatically** — it's part of shipping, not an optional follow-up.
3. Announce each deploy before running it (one-line `Running <command> because <path> changed`).
4. Stream the deploy output so the user can spot failures. If the deploy fails, surface the error and stop — do not retry blindly or hide the failure behind a summary.
5. If a rule is ambiguous or the deploy is destructive/irreversible beyond a normal code push (e.g., DB migrations against prod, infra teardown), confirm with the user before running.
6. If no rules match the committed paths, skip step 13 silently.

---

## AWS SAM deploy (Lambda / CloudFormation)

Most common fleet pattern for personal projects with an `aws/` directory.

### When to run

After a successful push to `main`, when **any** committed file matches a trigger path documented in the repo's AGENTS.md. Typical triggers:

| Path prefix | Why |
| --- | --- |
| `aws/template.yaml`, `aws/template.yml` | Stack definition, env vars, alarms, IAM |
| `aws/deploy.sh` | Deploy script / bundling behavior |
| `src/handlers/` | Lambda handler entrypoints |
| `src/lib/` | Shared code bundled into Lambdas |

**Important:** `src/lib/` changes often require SAM redeploy even when handlers are unchanged — the bundled artifact includes shared modules. Do not skip SAM deploy just because only `src/lib/` changed.

### Preconditions

1. **Code must be on `main` first** (step 11 done). Feature-branch SAM deploy before merge can push partial env vars to production and crash Lambdas. See project `docs/deploy-gotchas.md`.
2. **AWS credentials** must work locally (`AWS_PROFILE` per `docs/tooling-setup.md` or AGENTS.md). If deploy fails with SSO expiry, stop and ask the user to `aws sso login` — do not switch profiles or IAM users silently.
3. **`aws/samconfig.toml`** is usually gitignored — user must have copied `samconfig.toml.example` once. If deploy fails with missing config, surface that setup step; do not invent profile names.

### Command (pick what the repo documents)

```bash
# Preferred when package.json defines it (StockTextAlerts, etc.)
npm run deploy:aws

# Or directly
cd aws && npm run deploy

# Generic SAM (when no npm wrapper)
cd aws && sam build && sam deploy
```

Run from the **repo root** unless AGENTS.md says otherwise. Do not use `--no-verify` on git; SAM flags follow project `deploy.sh`.

### Success criteria

- Command exits 0.
- Output shows stack update complete (wording varies: `UPDATE_COMPLETE`, `Successfully created/updated stack`).
- Include deploy status in step-14 summary: `AWS SAM deploy: succeeded` or `failed`.

### Reference: StockTextAlerts

From root `AGENTS.md`:

- **Triggers:** `aws/template.yaml`, `aws/deploy.sh`, `src/handlers/`, `src/lib/`
- **Command:** `npm run deploy:aws` (alias for `npm --prefix aws run deploy`)
- **Gotcha:** merge env-var template changes to `main` before SAM deploy — see `docs/deploy-gotchas.md`

---

## Common patterns (other stacks)

**SAM/CloudFormation** — see **AWS SAM deploy** above (preferred detail).

**CDK**:

- Trigger: changes to `*.cdk.ts`, `cdk.json`, or `bin/<app>.ts`.
- Command: `cd <cdk-dir> && cdk deploy`.

**Terraform**:

- Trigger: changes to `*.tf`, `*.tfvars`.
- Command: `cd <tf-dir> && terraform apply` (with explicit user confirmation for destroys).

**Lambda code-only updates** (when CI handles infra but not code):

- Trigger: changes to handler source files in a path documented in AGENTS.md (e.g., `src/handlers/**`).
- Command: project-specific (often the GitHub Actions workflow handles this on push; if AGENTS.md says so, **skip** manual SAM deploy for handler-only changes).

**Docker image pushes**:

- Trigger: changes to `Dockerfile`, `docker-compose.yml`.
- Command: project-specific build + tag + push sequence.

## Avoiding the trap

The most common bug here is **skipping deploy because the orchestrator treated it as optional**. Examples:

- Changed `src/handlers/email-dispatch.ts` and pushed — Lambda still runs old code until SAM deploy runs.
- Changed `src/lib/messaging/` shared by Lambdas — same; CI may not redeploy Lambdas automatically.

The second-most-common bug is **running SAM deploy before merge to `main`** when env vars changed — partial production config.

Mitigation:

- Step 13 runs deploy automatically when path triggers match.
- When the deploy is destructive (DB drops, infra teardown, prod resource deletes), confirm with the user before running.
- When credentials fail, stop and ask — do not pretend deploy succeeded.
