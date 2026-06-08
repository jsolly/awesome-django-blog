# SEO issue triage

Classify by user impact and ownership, not by the crawler's category label.

## Tiers

| Tier | Meaning | Typical action |
| --- | --- | --- |
| P0 | Critical indexing/crawl failure on important public pages | Fix now, deploy, re-verify |
| P1 | Actionable code/config defect likely to affect crawl/indexing or search appearance | Fix in current session when scoped |
| P2 | Useful improvement or low-risk warning | Batch or schedule |
| P3 | Informational, accepted noise, third-party, or not code-owned | Document, do not patch |

## P0 examples

- Public revenue or landing page has accidental `noindex`.
- Important public page blocked by `robots.txt`.
- Redirect loop or long redirect chain prevents final 200 response.
- Canonical points to a redirected, blocked, or wrong-host URL and GSC confirms indexing trouble.
- Sitemap excludes primary public pages or lists only redirecting/private URLs.

## P1 examples

- Wrong canonical host across public pages.
- Sitemap includes admin, auth-gated, or noindex pages.
- Stale internal links point at redirects or 404s.
- Duplicate/missing titles or meta descriptions across important public templates.
- Code-owned redirect chain can be flattened safely.
- GSC indexed URL now returns 404/410 without an intentional removal path.

## P2 examples

- Missing social tags.
- Thin or short meta descriptions on low-value pages.
- Missing image alt text where not accessibility-critical.
- Short redirect chain on low-importance URL with internal-link cleanup available.
- Non-critical performance SEO warnings.

## P3 examples

- HTTP to HTTPS redirect resolving cleanly.
- Apex to `www` or `www` to apex canonical host redirect resolving cleanly.
- External pages controlled by third parties.
- Ahrefs compare-baseline "New" rows after a legitimate host/canonical change.
- Protected/private pages intentionally noindexed and absent from sitemap.
- Crawl noise with no internal inlinks and no GSC indexing problem.

## False-positive filters

Apply these before proposing code changes:

1. **Redirect noise:** If the redirect is HTTP to HTTPS or apex/`www` normalization, resolves to the canonical 200 page, and has no stale internal inlinks, classify P3.
2. **Chain ownership:** If a chain includes a code-owned redirect or stale internal link, classify by the code-owned segment, not the hosting redirect.
3. **External pages:** Treat external-page issues as P3 unless the codebase links to a bad external URL that should be updated.
4. **Structured data:** Static HTML absence is not proof. Verify rendered HTML or a rich-results style tool before classifying P0/P1.
5. **Noindex intent:** Determine whether the page is public, private, temporary, or account-gated before changing `noindex`.
6. **Cache lag:** Immediately after deploy, verify live URL output and cache headers before declaring a crawler result stale or unresolved.
7. **GSC cross-check:** If a crawler reports 4xx/5xx, inspect whether Google has the URL indexed and whether the issue is transient, blocked, or bot-specific.

## Root-cause map

| Finding | Likely code/config surface |
| --- | --- |
| Wrong canonical | Head component, SEO helper, site URL env, framework config |
| Sitemap redirect/private URL | Sitemap generator, route exclusion list, canonical host config |
| Robots blocking public pages | `robots.txt`, route-specific headers, deploy config |
| Accidental noindex | Head component, auth-gated layout, `X-Robots-Tag` header |
| Broken internal link | Navigation config, content source, route rename |
| Code-owned redirect chain | Framework redirects, server config, Cloudflare/Vercel rules |
| Duplicate title/meta | Template defaults, dynamic page metadata |
| IndexNow suggestion | Hosted key file, Ahrefs crawl setting, changed public URL list |

## Decision prompt

For each issue, be able to say:

> This is `[tier]` because `[evidence]`. The owner is `[code/config/infrastructure/content/third-party]`. The next action is `[fix/document/ask/wait]`.

If that sentence is not clear, gather more evidence before editing.
