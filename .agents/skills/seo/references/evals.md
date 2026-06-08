# SEO skill evals

Use this file before changing `SKILL.md` frontmatter. If a description change alters expected routing, update these cases in the same changeset.

## Positive load cases

The `seo` skill should load for:

- `/seo audit this site with Ahrefs and fix anything actionable`
- `/seo stocktextalerts.com`
- `/seo https://www.stocktextalerts.com`
- `Run Ahrefs Site Audit, inspect all issues, and remediate the codebase`
- `Use Google Search Console to check whether these fixed URLs are indexed`
- `Submit the sitemap and changed URLs after the SEO fixes deploy`
- `The sitemap has redirects and wrong canonicals; fix the source`
- `Ahrefs says canonical points to redirect; figure out if it is real`
- `Trigger another Ahrefs crawl and compare against the post-fix baseline`
- `Keep fixing, deploying, re-crawling, and scanning until the SEO score is 100 or stops improving`
- `Use Squirrel to get a before/after technical SEO crawl`
- `Submit these public URLs to IndexNow after deploy`
- `Robots.txt, sitemap, noindex, and canonical tags look wrong`

## Negative neighbor cases

The `seo` skill should not load for:

- `Research keywords for a new landing page`
- `Write a content calendar for our blog`
- `Improve this page copy for conversion`
- `Plan a backlink outreach campaign`
- `Review this PR for bugs before I push`
- `Make this page faster and improve Core Web Vitals only`
- `Run an accessibility audit`
- `Set up Google Ads conversion tracking`
- `Create Open Graph images for social sharing`
- `Analyze product-market positioning`

## Forbidden-load cases

- `/research SEO tools for SaaS startups` → use the research skill.
- `/review-fix-push-babysit ship the SEO changes` → use the review-fix-push-babysit skill.
- `Why are emails going to spam?` → not SEO; use email/deliverability guidance if available.
- `Build a new marketing landing page` → use frontend/design or product-marketing guidance, not `seo`, unless the user specifically asks for technical SEO audit/fix.

## Progressive-read expectations

- Read `orchestration.md` for any full audit/fix/verify run.
- Read `issue-triage.md` before classifying Ahrefs, GSC, or Squirrel findings.
- Read `tooling.md` when using the Ahrefs browser UI/export flow, optional Ahrefs API/MCP, GSC API/CLI, Squirrel CLI, browser verification, sitemap submission, or IndexNow.
- Read `report-template.md` before final reporting.
- Keep `SKILL.md` loaded but concise; do not inline detailed API or CLI reference there.

## Routing description target

Good description shape:

```yaml
description: Use when the user says `/seo`, including `/seo <website>`, or asks to audit, fix, or verify technical SEO issues involving Ahrefs, Google Search Console, Squirrel, IndexNow, sitemaps, robots.txt, canonicals, noindex, redirects, crawling, or indexing. Do NOT use for keyword research, content strategy, backlink outreach, paid search, generic performance, accessibility-only work, or code review.
```

Review the positive and negative cases before changing this text. The goal is high recall for technical SEO audit/fix/verify work and low spillover into marketing strategy or generic web quality tasks.
