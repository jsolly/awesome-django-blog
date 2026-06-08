---
description: Scenario-based testing philosophy and anti-flake patterns
globs: "**/*.{test,spec}.{ts,tsx,js,jsx,mjs,cjs},**/tests/**,**/__tests__/**"
alwaysApply: false
---

# Testing

## Philosophy

- **Scenario-based coverage**: Cover real-world scenarios that could happen in production — not to maximize code coverage or add a test file per source file. Each test should represent a plausible user journey or system event.
- **Integration over isolation**: Prefer integration tests that use real dependencies. Only mock external services that consume paid API allocations.
- **Assert via behavior, not mocks**: Prefer asserting on DB state, response payloads, and status codes rather than on mocked return values or call counts.
- **Realistic data**: Use values that could plausibly appear in production — `Sarah Chen` over `foo`, `45.7° at 3:42pm` over `100°`, `$1,247.83` over `$1000`. Specific, plausible test data both reads better in failures and catches more real bugs.
- **A test must be able to fail.** If changing the business logic it guards wouldn't break the test, it asserts nothing. Pin the outcome that matters — the row that must change, the status that must return — not a condition that holds no matter what the code does.

## Scenario-first descriptions

Frame `describe`/`it` blocks around user journeys or system events, not abstract technical operations.

- Good: `"A signed-in user updates their timezone and sees the next send time refresh"`
- Good: `"A cron job precomputes daily digest content for upcoming users"`
- Good: `"User in Pacific timezone receives market update after close"`
- Bad: `"returns true when input is valid"`
- Bad: `"calls helper function"`
- Bad: `"returns correct value when input is 2"`

## Assertions

Prefer assertions on behavior and persisted state:

- Response code/body
- Redirected location
- Updated DB rows
- Notification log entries

Avoid overfitting to implementation details (exact call counts) unless call count *is* the behavior.

## Flaky test anti-patterns

- Avoid boundary-time fixtures like `now - cooldown + 1000`; use clearly inside/outside windows (for example, half cooldown for reject-path, multiple cooldown windows for allow-path).
- Prefer behavioral invariants over fragile counters when testing shared tables. Assert the correct rows remain/delete, not exact global delete counts unless the dataset is fully isolated.
- Do not add sleeps or longer timeouts as a first fix for flakes. First remove nondeterminism (clock control, unique test IDs, deterministic fixtures).
