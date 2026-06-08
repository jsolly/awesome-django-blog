---
name: alert-hub-integration
description: Use when adding a new Lambda to a personal project that routes errors via alert-hub, when wiring CloudWatch alarms to the shared SNS topic, or when debugging "alarm fired but the email arrived unenriched". Triggers on SAM templates that import `AlertTopicArn`, on new `AWS::Serverless::Function` resources, and on `AWS::CloudWatch::Alarm` / `AWS::Logs::MetricFilter` edits in personal projects.
---

# Alert-Hub Integration

## Overview

Personal-project Lambdas route CloudWatch alarms through alert-hub: alarm → shared SNS topic → enricher Lambda → SES email to <john@jsolly.com>. The contract is split across two repos and ~7 conventions; missing any single piece silently degrades enrichment without an obvious failure mode.

**Source of truth:** `~/code/alert-hub/docs/adding-a-project.md` and `~/code/alert-hub/docs/architecture.md`. This skill is the integrator's pre-commit checklist + canonical SAM snippet — it does not replace those docs.

**Separate concern:** `~/code/dotagents/rules/errors-and-logging.md` governs WHAT logs at which level. This skill governs HOW the resulting `level=error` lines reach the inbox.

## When to use

- Adding a new Lambda to an existing alert-hub-wired SAM template.
- Adding new alarms to an existing Lambda.
- Debugging an unenriched alarm email or a missing recovery email.
- Reviewing existing alarm wiring before deploy.

Skip when onboarding a brand-new project — read `~/code/alert-hub/docs/adding-a-project.md` end-to-end first, then come back here for the per-Lambda template.

## Canonical SAM snippet

For each new Lambda, add four resource families. Replace `<Name>` with the function's logical ID and `<project>` with the project's namespace (matches `FunctionName` prefix).

```yaml
<Name>Function:
  Type: AWS::Serverless::Function
  Properties:
    FunctionName: <project>-<name>
    LoggingConfig:
      LogGroup: !Ref <Name>LogGroup
    # ... rest unchanged ...

# Auto-created log groups use the function's logical ID + random suffix,
# which the enricher's prefix discovery (/aws/lambda/<project>) misses.
<Name>LogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /aws/lambda/<project>-<name>
    RetentionInDays: 30

<Name>ErrorLogFilter:
  Type: AWS::Logs::MetricFilter
  Properties:
    LogGroupName: !Ref <Name>LogGroup
    FilterPattern: '{ $.level = "error" }'
    MetricTransformations:
      - MetricNamespace: <project>     # SAME for every Lambda in the project
        MetricName: ErrorLogCount
        MetricValue: "1"
        DefaultValue: 0

<Name>FunctionErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: <project>-<name>-lambda-errors
    AlarmDescription: <Name>Function threw / timed out / OOMed
    Namespace: AWS/Lambda
    MetricName: Errors
    Dimensions:
      - Name: FunctionName
        Value: !Ref <Name>Function
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
    TreatMissingData: notBreaching
    AlarmActions: [!Ref AlertTopicArn]
    OKActions: [!Ref AlertTopicArn]

# Only if the Lambda is invoked by ScheduleV2/SQS/EventBridge.
<Name>Function<EventName>FailureAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: <project>-<name>-invocation-failures
    AlarmDescription: <Name>Function<EventName> failed to invoke target
    Namespace: AWS/Scheduler         # passthrough — see checklist row 6
    MetricName: TargetErrorCount
    Dimensions:
      - Name: ScheduleGroup
        Value: default
      - Name: ScheduleName
        Value: <Name>Function<EventName>
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
    TreatMissingData: notBreaching
    AlarmActions: [!Ref AlertTopicArn]
    OKActions: [!Ref AlertTopicArn]
```

The project-level `AlertTopicArn` parameter and aggregate `ErrorLogAlarm` (which pages on `<project>/ErrorLogCount` across all Lambdas) should already exist; if not, copy from `~/code/family-memory/aws/template.yaml` or `~/code/stocktextalerts/aws/template.yaml`.

If the Lambda calls upstream vendor APIs (Massive, Finnhub, etc.), also see the vendor-retry exclusion pattern at the bottom of `~/code/stocktextalerts/aws/template.yaml` — a per-Lambda `<Name>VendorRetryFilter` + alarm, subtracted from the aggregate `ErrorLogAlarm` via metric math, prevents a single vendor blip from paging on the global alarm. Pure DB→SES Lambdas don't need it.

## Integration checklist

| # | Item | Silent failure mode if missed |
| --- | --- | --- |
| 1 | `AlertTopicArn` resolves `/alert-hub/alert-topic-arn` from SSM | Stack-level lookup is loud, but per-alarm wiring is silent — alarms with no `AlarmActions` deploy fine and never page. |
| 2 | EVERY alarm has both `AlarmActions` and `OKActions` → `!Ref AlertTopicArn` | No recovery email — alarm fires once, then you never learn it cleared. |
| 3 | Explicit `AWS::Logs::LogGroup` named `/aws/lambda/<FunctionName>` | Auto-created groups (`/aws/lambda/<StackName>-<LogicalId>-<random>`) miss the prefix scan. Alarms fire UNENRICHED. |
| 4 | Custom metric namespace = project name (matches `FunctionName` prefix) | Enricher's `DescribeLogGroups({ logGroupNamePrefix: "/aws/lambda/<namespace>" })` returns nothing. Alarms fire unenriched. |
| 5 | Logger emits `{ "level": "error", "error": { "name": ..., "message": ... } }` JSON to stdout | `extractErrorSummary` can't surface the cause in the email body — operator opens CloudWatch to find anything useful. (`LogFormat` unset → CloudWatch defaults to the text format the enricher parses.) Pass page-worthy failures as `logger.error(message, context, err)` always; never `context.error`. Use `createErrorForLogging(caught)` (stocktextalerts) or pass Postgrest/errors directly. |
| 6 | `AWS/Scheduler` / `AWS/SQS` / `AWS/Events` alarms are passthrough by design | Don't expect log enrichment on these — `INFRASTRUCTURE_NAMESPACES` skips them. The plain alarm body is the whole signal. |
| 7 | No alarm name contains the substring `alert-hub` | Recursion guard turns it into passthrough-only (a self-alarm could re-trip the enricher's own ERROR filter). Pick a different word: `alert-pipe`, `alarms`, etc. |
| 8 | Every alarm has an explicit `AlarmName` | Generated names are unstable in email subjects and harder to grep in runbooks. |
| 9 | Metric-math aggregate alarms list underlying metrics with project namespace | alert-hub discovers log groups from `Trigger.Metrics[].MetricStat.Metric.Namespace` (and `FunctionName` dimensions). Keep namespaces aligned with `/aws/lambda/<project>-*` log group prefixes. |
| 10 | Downstream `docs/alert-hub.md` lists enriched vs passthrough alarms | Operators and agents know whether to expect `log:` or only `log-groups` + lookup lines / short reason. |
| 11 | Downstream `docs/alert-hub.md` documents agent email lookup lines | Operators paste `insights-query` / `insights-query-request` from the email instead of guessing. |

## Common mistakes

- **Letting SAM auto-create the log group.** Default name doesn't match the prefix scan; enrichment silently fails.
- **Different metric namespace per Lambda.** Use one project-wide namespace; the enricher scans by prefix.
- **`AlarmActions` only, no `OKActions`.** No recovery email = stale mental model of what's still broken.
- **Importing the `family-memory` shared logger directly into a Vue-bundled project.** stocktextalerts has a bespoke logger at `src/lib/logging/` that's API-compatible but adds a `process` guard for browser builds — copy from there, don't sync from `~/code/family-memory/src/shared/logging.ts`.
- **Adding new alarms but forgetting the aggregate `ErrorLogAlarm` already covers them.** Per-Lambda `AWS/Lambda Errors` alarms catch thrown exceptions / timeouts / OOMs; the aggregate `ErrorLogAlarm` catches structured `level=error` log lines that didn't throw. Both exist on purpose; don't dedupe one away.
- **Metric math without project-scoped namespaces in `Trigger.Metrics[]`.** The enricher won't find `/aws/lambda/<project>-*` groups; emails fall back to threshold text only.
- **Expecting `log:` on every alarm.** When Insights finds no error line but log groups were inferred, emails include `log-groups` plus agent lookup lines (`region`, `account`, `alarm-name`, `time-start` / `time-end`, `insights-query`, optional `insights-query-request` when `request-id` is present) — still agent-actionable. Playbook: `~/code/alert-hub/docs/architecture.md` → **Agent log lookup playbook**.

## Cross-references

- `~/code/alert-hub/docs/adding-a-project.md` — onboarding (read once per new project).
- `~/code/alert-hub/docs/architecture.md` — log-group discovery, recursion guard, `INFRASTRUCTURE_NAMESPACES`.
- `~/code/alert-hub/docs/adding-a-project.md` — logging/alarm onboarding for downstream SAM apps.
- `~/code/alert-hub/docs/architecture.md` — **Agent log lookup playbook** (machine-readable email lines).
- `~/code/dotagents/rules/errors-and-logging.md` — separate concern: when to log at `info`/`warn`/`error`, including bounded payload logging.
- Reference templates: `~/code/stocktextalerts/aws/template.yaml`, `~/code/family-memory/aws/template.yaml`.
