---
description: Core code style — clarity over flexibility, no shims, no barrel files
alwaysApply: true
---

# Code Style

Optimize for clarity now over flexibility later. Fewer abstractions, fewer dependencies, fewer flags.

- **Write directly against the current API.** No shims, adapters, deprecation wrappers, or re-exports for legacy behavior.
- **Target the modern web baseline.** Modern browser APIs (`fetch`, `URL`, `AbortController`, `crypto.randomUUID()`, etc.) are assumed; no polyfills. Server-side polyfills are fine when Node.js lacks the API.
- **Use relative imports.** No `@`-style aliases.
- **Import from the defining module.** No barrel files or re-export aggregators.
- **Fix race conditions at the root.** Don't mask them with `setTimeout`/`nextTick`/`requestAnimationFrame`. Debouncing and throttling are fine.
- **Delete the old shape when you change a shape.** Parse only fields the code actually reads; drop branches that handled prior shapes.
- **Drop unused schema fields.** Schemas describe what the code uses today, not hypothetical past or future clients.
- **Edit schemas in place during prototyping; recreate the DB.** Write migration files only after the schema is shipped to a real environment.
- **Ship features behind real architectural seams** (separate endpoints, separate code paths) rather than runtime feature flags.
- **Use git history as the archive.** Delete dead code instead of commenting it out.
- **Prefer deep refactoring over preserving backwards compatibility.**
