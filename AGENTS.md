# AGENTS.md

## Project Rules

- Add project-specific rules above or below the managed global block.

<!-- BEGIN GLOBAL RULES (managed by sync-global-agents.sh) -->
## Family Memory

When the family-memory MCP is available, call `recall` (no args) at conversation start to load context about the user. Use `remember` to store notable new facts, preferences, or events that come up naturally.

## Collaboration

- Use `--headed --persistent` when launching playwright-cli for interactive browser sessions. Without `--headed`, it defaults to headless.
- No pull requests for personal projects. `/review-fix-push` skill is the sole review gate — reviews local changes against remote, fixes issues, commits and pushes.
- Custom skills live at `~/.agents/skills/` (e.g., `~/.agents/skills/review-fix-push/SKILL.md`), not `.claude/plugins/`.
- `~/.cursor/skills/` and `~/.claude/skills/` must be **real directories** (not symlinks to `~/.agents/skills/`). The `npx skills add` installer stores content in `~/.agents/skills/<name>/` then creates per-skill symlinks from each agent dir — directory-level symlinks cause circular links.
- Family/domain knowledge lives in the family-memory MCP, not in flat files.
- Don't create new IAM users or roles when an existing one can be reused — these are personal projects, avoid role sprawl.
- Always run `sam deploy` after modifying `aws/template.yaml` — there's no CI for SAM stacks, only code-only updates deploy via GitHub Actions.

## AWS

- Use `--profile prod-admin` for all production AWS commands.
- SSO profiles: `prod-admin` (730335616323, production), `general-admin` (541310242108), `amplify-admin`, `jsolly-sandbox`, `jsolly-dev`.

## Error Logging & alert-hub

**Goal.** Every uncaught exception or `level=error` log entry from any personal-project Lambda lands in a single email inbox with the actual error text — no need to open CloudWatch.

### Pipeline

```
Lambda (structured JSON logger)
  -> CloudWatch Logs (/aws/lambda/<FunctionName>)
  -> CloudWatch Alarm (AWS/Lambda Errors  AND  custom MetricFilter on level=error)
  -> SNS topic (alert-hub-notifications, ARN at SSM /alert-hub/alert-topic-arn)
  -> alert-hub Enricher Lambda (~/code/alert-hub/aws/enricher/handler.py)
  -> Logs Insights pulls the matching log group's recent error lines
  -> SES email with alarm header + extracted error summary + raw alarm JSON
```

The enricher is best-effort: a Logs Insights timeout or missing log group falls through to a plain passthrough email so an alarm is **never** silenced.

### Downstream Lambda contract

Every Lambda that publishes alarms to alert-hub must:

1. **Use the structured logger.** Never `console.log`/`console.error` in app code.
   - Node source of truth: `~/code/family-memory/src/shared/logging.ts` (port verbatim into other Node repos and keep them in sync). PII masking (phones/emails/tokens), sensitive-key redaction, stable JSON shape.
   - Python: rely on the runtime's `LogFormat: JSON` and `logger.error()` / `logger.exception()`. Logger emits uppercase `"ERROR"` level.
2. **Explicit `AWS::Logs::LogGroup`** named `/aws/lambda/<FunctionName>` with `RetentionInDays: 30`. Wire on the function via `LoggingConfig.LogGroup: !Ref <LogGroup>`.
3. **Explicit `FunctionName`** on each `AWS::Serverless::Function` so the log group name is deterministic instead of `<stack>-<logical>-<hash>`. Hyphenated, repo-prefixed (`misc-notifications-morning-text`, `family-memory-memories`).
4. **Do not set `LogFormat: JSON` on Node Lambdas** — the app-level logger already emits structured JSON; the runtime wrapper would double-wrap. Python Lambdas DO set `LogFormat: JSON` (no app-level logger).
5. **Two alarms per Lambda, both wired to alert-hub** with `AlarmActions` AND `OKActions`:
   - **(a) `AWS::CloudWatch::Alarm` on `AWS/Lambda Errors`** (FunctionName dimension). Catches crashes, timeouts, OOM. Always discoverable by the enricher.
   - **(b) `AWS::Logs::MetricFilter` on `{ $.level = "error" }`** (Node) or `{ $.level = "ERROR" }` (Python) plus a custom-namespace alarm. Catches application-logged errors that didn't crash the invocation (e.g. swallowed per-recipient failure inside a `Promise.allSettled`).
6. **Custom metric namespace must align with the Lambda function-name prefix** so the enricher's prefix discovery (`describe_log_groups(prefix=/aws/lambda/<namespace>)`) finds the right log groups. Example: namespace `family-memory` → matches log groups `/aws/lambda/family-memory-*`. Drift here breaks enrichment for the metric-filter alarm.
7. **Logging contract test** (Node only — Python uses the runtime): `tests/logging-contract.test.ts` pins JSON shape, level values, and PII masking so the enricher's `extract_error_summary` keeps working.

Copy-paste starter that satisfies the contract: `~/code/alert-hub/templates/lambda-logging.yaml`.

### Logger usage

```ts
// Node — instantiate once per module with shared base context.
const logger = createLogger({ job: "morning-text" });

logger.info("Send claimed", { recipient: to, dateLocalIso });
logger.warn("Failed to fetch iCloud calendar", { subsystem: "caldav" }, error);
logger.error("Recipient send failed", { recipient: to }, error);
```

```py
# Python — Lambda runtime renders this as JSON via LogFormat: JSON.
logger.error("Failed to process record", extra={"recipient": to})
logger.exception("Unexpected failure")  # includes traceback
```

`error` argument is serialized via `serializeError` (Node) — `error.name`, `error.message`, `error.cause`, full stack — which is what the alert-hub enricher's `extract_error_summary` reads to render the email's "Error log lines" block.

### Logging levels (cross-repo)

- `info` — expected business rejections (auth failures, invalid input, rate limits) and routine lifecycle events.
- `warn` — early signals that could escalate to an error if ignored, or transient failures that the next retry / next scheduled invocation may recover from on its own.
- `error` — the failure can't be fixed by a retry, or retries have already exhausted. The data is wrong, the operation can't complete, the parser rejected input we expected to parse.

**Per-recipient / per-item error handling inside a fan-out:** wrap with `Promise.allSettled` (or equivalent), then **log each rejected reason at `error`** before re-throwing the aggregate. Lambda's runtime serializes only the top-level error message — without an explicit log-per-failure, the actual cause never reaches the enricher.

### alert-hub side

- **Enricher source:** `~/code/alert-hub/aws/enricher/handler.py`. Logs Insights query is `level = "error" or level = "ERROR"`, sorted desc, limit 20. Extraction parses Node tab-delimited JSON tail and Python-runtime JSON objects, surfacing `error.name + error.message` (or `stackTrace[:5]`).
- **Discovery:** AWS/Lambda alarms → `/aws/lambda/<FunctionName>` (deterministic). Custom namespace alarms → `describe_log_groups(prefix=/aws/lambda/<namespace>)`. `AWS/Scheduler|AWS/SQS|AWS/Events` alarms skip enrichment by design (no per-namespace log group).
- **Self-recursion guard:** any `AlarmName` containing `alert-hub` is passthrough-only, even on `OK` recovery. Prevents the enricher's own metric filter from looping.
- **IAM:** enricher has `logs:StartQuery`, `logs:GetQueryResults`, `logs:DescribeLogGroups` on `*` because it serves arbitrary downstream stacks.

### Adding a new project

1. Resolve the topic ARN in the SAM template:
   ```yaml
   AlertTopicArn:
     Type: AWS::SSM::Parameter::Value<String>
     Default: /alert-hub/alert-topic-arn
   ```
2. Copy the relevant blocks from `~/code/alert-hub/templates/lambda-logging.yaml` (LogGroup + MetricFilter + both alarms).
3. Pick a custom MetricNamespace that matches your Lambda function-name prefix.
4. If publishing alerts directly from app code (not just via alarms), grant `sns:Publish` on `!Ref AlertTopicArn` to the function role.
5. Use the structured logger and emit `level=error` for non-recoverable failures.

## User Context

Software engineer turned Sr. Director at Leidos (Health-IT under DIGMOD). I use this chat to think through ideas, explore topics, write code, and have real conversations.

When exploring ideas, be discursive and collaborative — follow the thread wherever it goes, even if it gets uncomfortable. Steel-man arguments, don't lecture. When I'm vague, call it out directly. When my logic doesn't hold up, say so. I'd rather be challenged than reassured. I value extreme bluntness, the proactive surfacing of things I haven't considered, and getting closer to the truth over reaching a comfortable answer.

## Conversation Preferences

- **Ask when ambiguous.** If there's one obvious approach, just do it. If there are meaningful tradeoffs or multiple paths, stop and ask.
- **Layered questions.** Ask the 2-3 most critical questions first, start on what's clear, then follow up as you go.
- **Present options with a recommendation.** "Here are approaches X, Y, Z. I'd recommend Y because..." — then wait.
- **Brief rationale.** A sentence or two on the "why" is enough. Don't belabor it.
- **Casual and direct.** Like a coworker on Slack. No hedging, no filler.
- **Do what I asked, but flag concerns.** If you think the approach has issues, implement it and note the concern — don't silently diverge.
- **Update at the end.** Show the result when done. Only interrupt mid-task if blocked.
- **Proactively improve adjacent code.** If you see something nearby that could be better, clean it up. Prefer deep refactoring over preserving backwards compatibility.
- **Concise responses.** Short, dense with information. I can ask for more detail.
- **When uncertain, ask.** Don't guess at project conventions, intent, or technical details — even if it slows things down.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`

Common types: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `perf`. Scope is the area of the codebase (e.g., `auth`, `notifications`, `e2e`, `deps`).

## Code Style

- **No compatibility layers**: No shims, adapters, deprecations, or re-exports for legacy behavior.
- **No browser polyfills**: Modern browser APIs (`fetch`, `URL`, `AbortController`, `crypto.randomUUID()`, etc.) are assumed. Server-side polyfills are fine when Node.js lacks the API.
- **Relative paths only**: No `@`-style aliases.
- **No barrel files / re-exports**: Import from the defining module, not intermediary files.
- **No timing hacks**: No `setTimeout`/`nextTick`/`requestAnimationFrame` to mask race conditions. Fix the root cause. Legitimate uses (debouncing, throttling) are fine.

## Error Handling

- **Trust the type system**: Skip defensive null/undefined checks when strict TypeScript or DB constraints guarantee safety. Add checks only when values can legitimately be missing (parsed JSON, nullable columns, third-party payloads).
- **Deterministic error checking**: Use structured error properties (`error.code`, `error.status`), not string matching (`.includes()`) on messages.
- **Fail fast**: No silent fallbacks or default values on unexpected errors. If a fallback is needed for resilience, gate it on structured error properties and log with context.
- **Logging levels**:
  - `info` — expected business rejections (auth failures, invalid input, rate limits) and routine lifecycle events.
  - `warn` — early signals that could escalate to an error if ignored, or transient failures that the next retry / next scheduled invocation may recover from on its own.
  - `error` — the failure can't be fixed by a retry, or retries have already exhausted. The data is wrong, the operation can't complete, the parser rejected input we expected to parse.

## Testing Philosophy

- **Scenario-based coverage**: Cover real-world scenarios that could happen in production — not to maximize code coverage or add a test file per source file. Each test should represent a plausible user journey or system event.
- **Integration over isolation**: Prefer integration tests that use real dependencies. Only mock external services that consume paid API allocations.
- **Assert via behavior, not mocks**: Prefer asserting on DB state, response payloads, and status codes rather than on mocked return values or call counts.
- **Realistic data**: Use real names, realistic values, and plausible details. Never use placeholder values like `foo`, `bar`, `test123`, or round numbers when a realistic value would work.
- **Scenario-based test style**: Frame `describe`/`it` blocks around user journeys or system events, not abstract technical operations.
  - Good: `"User in Pacific timezone receives market update after close"`
  - Bad: `"returns correct value when input is 2"`
<!-- END GLOBAL RULES (managed by sync-global-agents.sh) -->
