# Per-Project Post-Commit Deploys (Step 12)

Some projects require extra deploy steps after pushing because CI doesn't cover every path — e.g., SAM/CDK stacks, Terraform, Docker image pushes, Lambda code updates, manual cache invalidations.

This file documents the patterns; the actual rules per repo live in each project's `AGENTS.md`.

---

## How to detect which apply

In step 3 (load guidelines), the orchestrator notes any post-commit deploy rules gated on specific paths. Examples:

- "Always run `sam deploy` after modifying `aws/template.yaml`."
- "Run `terraform apply` from `infra/` after any `*.tf` change."
- "Lambda code-only updates to `src/handlers/` are deployed by the `Deploy Website` GitHub Actions workflow's `deploy-lambdas` job — no manual step needed."

The pattern is: **paths trigger commands**.

## How to execute (step 12)

After the push succeeds (step 11):

1. Re-check the post-commit deploy rules captured in step 3 against the list of committed files (`git diff --name-only origin/main~1 HEAD`).
2. If any rule's path trigger matches a committed file, **run the deploy command automatically** — it's part of shipping the change, not an optional follow-up.
3. Announce each deploy before running it (one-line `running <command> because <path> changed`).
4. Stream the deploy output so the user can spot failures. If the deploy fails, surface the error and stop — do not retry blindly or hide the failure behind a summary.
5. If a rule is ambiguous or the deploy is destructive/irreversible beyond a normal code push (e.g., DB migrations against prod, infra teardown), confirm with the user before running.
6. If no rules match the committed paths, skip step 12 silently.

## Common patterns

**SAM/CloudFormation**:

- Trigger: changes to `template.yaml`, `template.yml`, or `samconfig.toml`.
- Command: `cd <stack-dir> && sam build && sam deploy`.

**CDK**:

- Trigger: changes to `*.cdk.ts`, `cdk.json`, or `bin/<app>.ts`.
- Command: `cd <cdk-dir> && cdk deploy`.

**Terraform**:

- Trigger: changes to `*.tf`, `*.tfvars`.
- Command: `cd <tf-dir> && terraform apply` (with explicit user confirmation for destroys).

**Lambda code-only updates** (when CI handles infra but not code):

- Trigger: changes to handler source files in a path documented in AGENTS.md (e.g., `src/handlers/**`).
- Command: project-specific (often the GitHub Actions workflow handles this on push; if so, no manual step).

**Docker image pushes**:

- Trigger: changes to `Dockerfile`, `docker-compose.yml`.
- Command: project-specific build + tag + push sequence.

## Avoiding the trap

The most common bug here is **running a destructive deploy because the orchestrator didn't notice the rule was conditional**. Examples:

- "Run `sam deploy` after modifying `template.yaml`" but the diff only modified comments. Deploy is a no-op but still costs time.
- "Run `terraform apply`" but the diff added a resource that requires manual approval first.

Mitigation: when the deploy is destructive (DB drops, infra teardown, prod resource changes), always confirm with the user before running. The skill is for code; "I changed the schema and now it's deployed" should not be a surprise.
