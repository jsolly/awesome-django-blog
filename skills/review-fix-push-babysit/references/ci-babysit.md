# CI Babysit — Post-Push GitHub Actions Loop (Step 12)

After step 11 puts code on `main`, step 12 watches GitHub Actions for the pushed commit, fixes failures caused by the change, and pushes again until CI is green or the cycle cap is hit. Manual deploys (step 13) run only after CI passes or CI is absent.

Pre-push local reproduction (step 4, `references/conflict-resolution.md`) is still preferred — babysit covers what only runs on GitHub after push.

---

## Prerequisites (before step 11 push)

If `.github/workflows/` exists and the remote is GitHub:

1. Verify `gh auth status` succeeds.
2. Verify `gh workflow list --limit 20` returns workflows.

If authentication is missing, **stop before pushing** and ask the user to run `gh auth login`. Do not push and then discover babysit is impossible.

If `gh auth status` fails **during** babysit (after push), stop monitoring, report that CI status is unverified, and ask the user to re-authenticate before retrying babysit.

If no `.github/workflows/` directory exists, skip step 12 entirely — note `CI: skipped (no workflows)` and proceed to step 13.

---

## Detect CI runs for the pushed commit

After step 11 push:

```bash
SHA=$(git rev-parse HEAD)
gh run list --commit "$SHA" --json databaseId,name,status,conclusion,workflowName,event --limit 20
```

Filter to `event == push` (or `workflow_dispatch` if user-triggered). Ignore unrelated `pull_request` runs.

**Which workflows to wait on:**

- **Default:** all push-triggered runs for `$SHA`.
- **If AGENTS.md names guard workflows** (e.g., "Deploy Website", "CI", "Fleet"), prefer that list.
- **If branch protection defines required checks**, read them via `gh api repos/{owner}/{repo}/branches/main/protection` when available.

---

## Wait for completion

Per run (or pick the slowest guard workflow first):

```bash
gh run watch <run-id> --exit-status
```

Poll alternative if `watch` is unavailable:

```bash
gh run view <run-id> --json status,conclusion -q '.status + " " + (.conclusion // "")'
```

**Wall-clock ceiling:** ~45 minutes total babysit time. If exceeded, stop and report which runs are still pending.

---

## On failure — diagnose

```bash
gh run view <run-id> --log-failed
```

Pull only failed job logs — not full JSON dumps.

---

## Fix scope

- Fix failures **caused by this push's changes**.
- **Never** weaken CI/workflows to make red green.
- **Never** make unrelated code changes to paper over failures.
- If failure looks upstream/unrelated: `git fetch origin main` → check if `origin/main` advanced → **re-run step 2 sync** → re-smoke → push → re-watch. Another push may have fixed it.
- If failure is clearly unrelated and `origin/main` is unchanged, **stop and report** — don't thrash.

---

## Fix → commit → push → re-watch

Lighter than the pre-push loop:

1. Fix locally.
2. Re-run step 4 smoke (tests + types; `act` if CI/workflow files changed).
3. **Skip steps 6–8** (full agent fleet) unless failure is ambiguous or security-sensitive.
4. Stage by name, commit (`fix(ci): …`), push (`git push origin HEAD:main`).
5. On non-fast-forward: re-run step 2, smoke, push again (same rule as orchestration step 11).
6. Return to "Detect CI runs" with new `$SHA`.

**Loop bound:** 3 CI fix cycles. On the 4th failure, stop with **`Pushed to main — CI failed (stopped)`**, include last failed job + log excerpt + cycles attempted. Do **not** claim "shipped."

---

## Push rejection / new main commits during babysit

| Situation | Action |
| --- | --- |
| `git push` rejected (non-FF) | Step 2 sync → step 4 smoke → push |
| CI fails, but `origin/main` has new commits not in local | Same — sync before fix push |
| CI fails on code you didn't touch, `origin/main` unchanged | Investigate logs; if clearly unrelated, **stop and report** |
| Concurrent push while watching | After green, verify `$SHA` is still `origin/main`'s tip: `git fetch && git rev-parse HEAD origin/main` |

---

## Record for step 14

Note CI outcome in the closing summary:

- `CI: green (<workflow names>)`
- `CI: skipped (no workflows)`
- `CI: failed (stopped after N cycles) — <last failed job>`
