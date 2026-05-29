# Merge Conflict Resolution + CI Reproduction

Detail for steps 2 (sync main) and 4 (smoke check) of the orchestration.

---

## Merge conflict resolution (step 2)

When `git merge origin/main` produces conflicts:

- **Pause and walk the user through resolution.** Show `git status` so they see the conflict set; resolve file-by-file with the conflict markers as the source of truth.
- **Stage each resolved file individually** (no `git add -A` — the deny rules also discourage this).
- **After resolving, run typecheck + tests** before completing the merge. Conflict resolution often introduces subtle issues (a hand-merged function signature that doesn't match what callers expect).

If the merge introduced regressions in test fixtures or signatures (common when upstream changed function signatures the topic branch's mocks rely on), fix them as part of the merge resolution, not as a follow-up commit.

Commit the merge with the default merge message — Conventional Commits doesn't apply to merge commits.

## CI reproduction with `act` (step 4)

Local tests pass in a warm, cached dev environment; CI runs from cold, in a container, with a different OS/arch and a stripped-down env. Catching CI-only regressions locally is drastically cheaper than push-and-wait loops.

**When to reproduce CI**:

If the repo uses `act` (check for `.actrc`, `scripts/ci/run-local-actions.sh`, or `package.json` scripts like `gha:local*`), run the relevant local workflow when the diff touches any of:

- `.github/workflows/**` or `.github/actions/**`
- Test harness or runners (`tests/setup.ts`, `tests/run-vitest.ts`, `playwright.config.ts`, `vitest.config.ts`, any `tests/helpers/**`)
- CI-invoked `package.json` scripts (`test`, `test:ci`, `test:smoke`, `test:e2e`, `build`)
- Build/runtime config (`tsconfig*.json`, `astro.config.*`, `next.config.*`, `vite.config.*`, etc.)
- Container/service config (`supabase/config.toml`, `docker-compose*.yml`, `Dockerfile*`)
- Dependency changes that move packages between `dependencies` and `devDependencies`

**Workflows `act` can't run**: typically anything gated on `github.actor != 'nektos/act'` or requiring real cloud creds. Reproduce the equivalent step with local env overrides instead.

Example: if CI's E2E step is `npm run test:e2e` with a specific env var set in `.github/actions/run-ci/action.yml`:

1. Back up `.env.local`.
2. Write those env vars verbatim.
3. Rerun `npm run test:e2e`.
4. Restore `.env.local`.

**Repos without `act` configured**: skip this step; just flag in the agent review that CI coverage is thinner than local.

**If you skip CI reproduction on a change that touches any of the paths above and CI then fails, that's on you.** Add it to the lessons list for the next run.
