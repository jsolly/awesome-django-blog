---
name: seo
description: Use when the user says `/seo`, including `/seo <website>`, or asks to audit, fix, or verify technical SEO issues involving Ahrefs, Google Search Console, Squirrel, IndexNow, sitemaps, robots.txt, canonicals, noindex, redirects, crawling, or indexing. Do NOT use for keyword research, content strategy, backlink outreach, paid search, generic performance, accessibility-only work, or code review.
effort: max
---

# SEO Audit, Fix, and Verification

Use this for technical SEO work where the expected output is evidence-backed fixes, not a generic SEO checklist.

## Required first reads

1. Read `references/evals.md` if you are changing this skill.
2. Read `references/orchestration.md` before any full `/seo` run.
3. Read `references/issue-triage.md` before classifying findings.
4. Read `references/tooling.md` before using Ahrefs, GSC, Squirrel, sitemap submission, IndexNow, or browser automation.
5. Read `references/report-template.md` before final reporting.

## Operating principle

Start from crawler/search-console evidence, classify findings before editing, fix only code/config defects, then verify after deployment with a fresh crawl or inspection.

Technical SEO has many false positives. Expected infrastructure redirects and search-tool diff noise are not bugs just because a crawler lists them.

## Optional website argument

`/seo <website>` sets the target site. Normalize bare domains by prepending `https://`, preserving paths only when the user provided one. Examples:

- `/seo stocktextalerts.com` → `https://stocktextalerts.com/`
- `/seo https://www.stocktextalerts.com` → `https://www.stocktextalerts.com/`

Still confirm the canonical host once live evidence is available; do not assume bare domain vs `www`.

## Workflow summary

1. **Confirm target context** — site URL, canonical host, Ahrefs project ID, GSC property, deployment path, and available credentials/tools.
2. **Collect baseline** — Ahrefs issues, Squirrel crawl where available, live `robots.txt`/sitemap/canonical checks, and GSC URL Inspection for high-priority URLs.
3. **Classify before fixing** — P0/P1/P2/P3 with evidence, not category names alone.
4. **Inspect the codebase** — route config, framework SEO helpers, sitemap generator, robots output, headers, redirects, and protected routes.
5. **Apply fixes conservatively** — only for actionable code/config defects; document accepted noise.
6. **Deploy only with explicit approval** — never deploy autonomously.
7. **Iterate when authorized** — wait for the deployed app, re-crawl/re-scan, then keep fixing only while the score improves and actionable issues remain.
8. **Re-crawl and compare** — use a post-fix baseline, not stale "Yesterday" diffs, then verify IndexNow/GSC/sitemap outcomes.
9. **Report evidence** — before/after counts, iteration scores, resolved issues, remaining issues, accepted noise, and manual follow-ups.

Full details: `references/orchestration.md`.

## Gotchas

- Ahrefs "New" rows can mean compare-baseline noise. Adjust the baseline before claiming regressions.
- HTTP to HTTPS and apex to `www` redirects are usually P3 if they resolve cleanly and have no stale internal links.
- Redirect chains are actionable when code-owned, long, looped, or caused by stale internal links. Do not flatten hosting-level canonicalization blindly.
- Do not verify structured data by grepping static HTML. Use rendered browser output or an external rich-results style check.
- Noindex pages are not automatically broken. Check whether they are intentionally private and whether they are discoverable through sitemap/internal links.
- Post-deploy crawler results can lag caches/CDNs. Verify live output before deciding a fix failed.
- Stop optimization loops at 100 or when the score stops improving. Do not patch P3 accepted noise just to chase a score.
- GSC performance metrics lag indexing changes; same-day verification should use URL Inspection and crawl evidence, not clicks/impressions.
- A missing API token is not an unavailable tool. Ahrefs's primary path is the logged-in browser UI (open `app.ahrefs.com/site-audit`, match the project to the target host); GSC's is `gcloud` ADC. Attempt those — and record Ahrefs Health Score as the primary baseline — before falling back to Squirrel-only, which is justified only by a login wall or a missing project.

## Helper scripts

Run scripts from this skill directory or pass explicit paths:

- `scripts/ahrefs-issues.mjs` — fetch Ahrefs issue JSON with `AHREFS_API_TOKEN`.
- `scripts/gsc-inspect.mjs` — inspect URL indexing status with a bearer token or service account.
- `scripts/squirrel-baseline.sh` — run named Squirrel baseline audits.
- `scripts/seo-triage.mjs` — normalize evidence into sorted tiered findings.

Each script supports `--help`. Scripts must write data to stdout and status/errors to stderr.

## Safety rules

- Never write credentials, API tokens, OAuth tokens, or service-account JSON into the repo.
- Never deploy, submit production data writes, or mutate external project settings without explicit user approval.
- Never treat external-page issues as codebase defects.
- Never delete redirect, noindex, or robots rules without checking index/crawl consequences.
- Never call work complete without fresh verification evidence.

## Maintenance

Skills are a routing tax. Future updates should usually append gotchas and eval cases. Change the frontmatter description only when `references/evals.md` demonstrates a load failure or spillover failure, and update the evals in the same change.
