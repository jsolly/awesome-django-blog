# AGENTS.md

## Project Test Rules

- Add project-specific test rules above or below the managed global block.

<!-- BEGIN GLOBAL TEST RULES (managed by sync-global-agents.sh) -->
# Test Suite Architecture

This project treats tests as production documentation for real user flows.
Each test should answer: **"what happened for a real user or system event?"**

## Folder structure

- `tests/api/` - API route behavior (`src/pages/api/**`)
  - `*.test.ts` focuses on happy-path and expected behavior.
  - `*.security.test.ts` focuses on invalid/unauthorized/rejected paths.
- `tests/lib/` - business logic and provider integration helpers (`src/lib/**`).
- `tests/pages/` - route rendering and page-level behavior.
- `tests/smoke/` - Playwright smoke tests for route and console sanity.
- `tests/e2e/` - end-to-end user journeys (serial, production-like).
- `tests/helpers/` - shared factories/builders and test environment utilities.

## Naming conventions

### Scenario-first descriptions

Write `describe`/`it` text as production-like stories:

- A signed-in user updates their timezone and sees the next send time refresh
- A cron job precomputes daily digest content for upcoming users
- Avoid: returns true when input is valid
- Avoid: calls helper function

### File names

- Keep file names aligned to route/module responsibility.
- Prefer route-based names for API tests:
  - `notification-preferences/current.test.ts`
  - `profile/time-format.test.ts`
  - `auth/sms/send-verification.security.test.ts`

## Shared helpers

Use shared helpers before creating one-off fixtures:

- `tests/helpers/test-user.ts` - create/cleanup users with realistic defaults.
- `tests/helpers/test-env.ts` - authenticated cookies and admin client.
- `tests/helpers/api-context.ts` - APIContext request/cookie builders for route handlers.
- `tests/helpers/cron.ts` - cron request builders with Authorization header.

## Assertions philosophy

- Prefer assertions on behavior and persisted state:
  - response code/body
  - redirected location
  - updated DB rows
  - notification log entries
- Avoid overfitting to implementation details (exact call counts) unless call count is the behavior.

## Realism requirements

- Use realistic ticker symbols (`AAPL`, `MSFT`, `SPY`), real timezones (`America/New_York`), and plausible user data.
- Avoid placeholder symbols and unrealistic values unless testing validation.

## Flaky test anti-patterns

- Avoid boundary-time fixtures like `now - cooldown + 1000`; use clearly inside/outside windows (for example, half cooldown for reject-path, multiple cooldown windows for allow-path).
- Prefer behavioral invariants over fragile counters when testing shared tables. Assert the correct rows remain/delete, not exact global delete counts unless the dataset is fully isolated.
- Do not add sleeps or longer timeouts as a first fix for flakes. First remove nondeterminism (clock control, unique test IDs, deterministic fixtures).
<!-- END GLOBAL TEST RULES (managed by sync-global-agents.sh) -->
