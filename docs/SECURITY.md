# Security policy

Report vulnerabilities privately using the contact in
[security.txt](https://www.blogthedata.com/.well-known/security.txt). Include the
public URL, reproduction steps and expected impact. Do not publish credentials,
private exports or exploit details in a public issue.

The app builds static public content; no reader accounts, comments or API keys
are shipped. Authored HTML is sanitized and script CSP hashes are emitted during
build. PagesCMS/GitHub permissions and production hosting remain separate trust
boundaries. Keep their repository grants narrow and production merges protected.

Dependency updates require CI and review. Existing AWS media permissions must not
be widened. See the [cutover and backup runbook](astro-migration.md) before changing
production hosting or retiring any old resources.
