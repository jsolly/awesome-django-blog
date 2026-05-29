---
description: Error handling and structured logging levels
globs: "**/*.{ts,tsx,js,jsx,mjs,cjs,py,go,rs,java,kt}"
alwaysApply: false
---

# Errors and Logging

## Error Handling

- **Trust the type system**: Skip defensive null/undefined checks when strict TypeScript or DB constraints guarantee safety. Add checks only when values can legitimately be missing (parsed JSON, nullable columns, third-party payloads).
- **Deterministic error checking**: Use structured error properties (`error.code`, `error.status`), not string matching (`.includes()`) on messages.
- **Surface unexpected failures.** Let errors propagate when there's no specific recovery path. Catching to substitute a default or hide a logic bug is a maintenance trap. Retries are appropriate only for structured transient failures (`error.code: 429`, network timeouts) — log at `warn` while retrying, escalate to `error` on exhaustion or non-retryable failures.

## Logging Levels

- `info` — expected business rejections (auth failures, invalid input, rate limits) and routine lifecycle events.
- `warn` — early signals that could escalate to an error if ignored, or transient failures that the next retry / next scheduled invocation may recover from on its own.
- `error` — the failure can't be fixed by a retry, or retries have already exhausted. The data is wrong, the operation can't complete, the parser rejected input we expected to parse.
