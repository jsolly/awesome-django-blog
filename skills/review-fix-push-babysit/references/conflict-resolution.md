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

## CI reproduction before push (step 4)

Local tests pass in a warm, cached dev environment; the default-branch deploy workflow runs from cold with production or cloud credentials. Catching regressions locally is drastically cheaper than push-and-wait loops. For this skill, step 12 CI babysit is the explicit post-push exception — pre-push local reproduction remains primary.

**Default:** run the repo's pre-commit hook (or the same commands it runs) before `git push origin HEAD:main`. That stack should match the non-deploy portion of the main guard workflow.

**When to run the full local guard**, especially if pre-commit is lighter than deploy:

- `.github/workflows/**` or `.github/actions/**`
- Test harness or runners (`tests/setup.ts`, `tests/run-vitest.ts`, `playwright.config.ts`, `vitest.config.ts`, any `tests/helpers/**`)
- CI-invoked `package.json` scripts (`test`, `test:ci`, `test:smoke`, `test:e2e`, `build`)
- Build/runtime config (`tsconfig*.json`, `astro.config.*`, `next.config.*`, `vite.config.*`, etc.)
- Container/service config (`supabase/config.toml`, `docker-compose*.yml`, `Dockerfile*`)
- Dependency changes that move packages between `dependencies` and `devDependencies`

**Deploy workflows with prod creds** (Vercel, linked Supabase, AWS Lambda publish) are not runnable locally. Reproduce their check steps via pre-commit or documented local commands; accept that the publish step only runs on GitHub after push.

**If you skip the full local guard on a change that touches any of the paths above and CI then fails, that's on you.** Add it to the lessons list for the next run.
