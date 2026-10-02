# Contributing

Use Node 24 and the pinned npm lockfile. Follow the [setup instructions](../README.md)
and [project instructions](../AGENTS.md). Make changes on a branch from current
`origin/main`, run `npm run gate`, and open a PR. Use Conventional Commits and
explain the resulting behavior and relevant validation. Required check: `CI / ci`.

Content edits follow [PagesCMS publishing](publishing.md). Keep published URLs,
category case, dates and author identity stable. Never commit private exports,
secrets or generated builds. UI changes need desktop/mobile verification with
screenshots and a clean console. Deployment changes need exact-release smoke.

See the [code of conduct](CODE_OF_CONDUCT.md). Report vulnerabilities privately
according to [the security policy](SECURITY.md).
