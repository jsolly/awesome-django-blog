# SEO tooling reference

Use the safest available path. Do not invent credentials or persist secrets.

## Ahrefs

Preferred order:

1. Browser UI in the user's logged-in Ahrefs session.
2. Browser UI exports when table data is too large to inspect manually.
3. Direct API with `AHREFS_API_TOKEN` only if the user explicitly has paid API access.
4. Ahrefs MCP only if already configured and available in the active agent environment.

Default assumption: no paid Ahrefs API. Manually navigate the Site Audit project, inspect issue rows, trigger crawls from the UI, set compare baselines, and submit IndexNow from the UI when available.

Use `scripts/ahrefs-issues.mjs` only for optional API reads. It requires `--project-id` and `AHREFS_API_TOKEN`.

Known constraints:

- Site Audit project ID is visible in Ahrefs URLs such as `/site-audit/<project-id>/...`.
- New full crawls should be triggered through the browser UI unless the user confirms another supported path.
- "New" issue rows depend on compare baseline. Use the most relevant crawl, not automatically "Yesterday".
- IndexNow submission in Ahrefs may require the crawl setting to know the key even if the key file exists on the site.

## Google Search Console

Use GSC for Google-side evidence:

- URL Inspection for indexed/canonical/robots/fetch state on selected URLs.
- Sitemaps API for submitting or re-submitting sitemap URLs.
- Search Analytics only for delayed performance follow-up, not same-day fix verification.

Credentials:

- Prefer `GSC_ACCESS_TOKEN` for a short-lived bearer token.
- `GOOGLE_APPLICATION_CREDENTIALS` service-account support depends on local OAuth/JWT availability and property permissions.
- If `gcloud` is installed, run ADC login once, set a quota project, then let `gsc-inspect.mjs` call `gcloud auth application-default print-access-token`:

```bash
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/webmasters
gcloud auth application-default set-quota-project YOUR_GCP_PROJECT_ID
node skills/seo/scripts/gsc-inspect.mjs --check-auth
```

Verify token retrieval (do not pass `--scopes` to `print-access-token`; scopes come from ADC login):

```bash
gcloud auth application-default print-access-token >/dev/null && echo "GSC auth ready"
```

The Search Console API also requires a quota project. If calls return 403 mentioning ADC or quota project, rerun `set-quota-project` with a project where Search Console API is enabled and your Google account has access to the GSC property.

- Never commit service-account JSON or OAuth tokens.

Use `scripts/gsc-inspect.mjs` for batch URL Inspection. Default cap should preserve quota; inspect a representative URL set instead of every crawled URL.

## Squirrel CLI

Use Squirrel as local technical crawl evidence, not as a replacement for Ahrefs/GSC.

Check availability:

```bash
squirrel self doctor
```

Use:

```bash
scripts/squirrel-baseline.sh pre https://example.com .seo-audit
scripts/squirrel-baseline.sh post https://example.com .seo-audit
```

Default to surface coverage. Escalate only when the user asks or the site size warrants it.

## Browser verification

Use browser tools for:

- Rendered head/canonical/meta/structured-data checks.
- Ahrefs UI crawls, settings, and compare baselines.
- GSC UI fallback when API credentials are unavailable.

Stop if blocked by login, CAPTCHA, permissions, destructive confirmation, or ambiguous account/project selection.

## Live HTTP checks

Directly verify:

- `robots.txt`
- sitemap index and child sitemaps
- canonical page HTML
- redirect chain and final status
- `X-Robots-Tag` headers
- IndexNow key file

Use crawler user agents only when diagnosing bot-specific behavior; do not rely on one user agent as universal truth.

## Sitemap submission

Submit via GSC only after:

- Sitemap URL is live and returns 200.
- Sitemap points to canonical public URLs.
- User has approved external mutation if required by the environment.

If GSC credentials are absent, provide exact manual UI steps instead.

## IndexNow

Submit only public canonical URLs that changed or were newly published.

Requirements:

- Key is known.
- Key file is hosted at the root of the canonical host and returns the key content.
- Payload host matches the canonical host.

Use direct API submission when Ahrefs UI is blocked, and report the HTTP status.

## Credential safety

- Read tokens from environment variables only.
- Print missing-variable names, never token values.
- Write machine-readable output to stdout and diagnostics to stderr.
- Avoid logging full page content when URLs or HTML may reveal private routes.
