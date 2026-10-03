# Astro migration and cutover

Production is live on Vercel at <https://www.blogthedata.com>. The reviewed replacement
landed on protected `main` in [PR #677](https://github.com/jsolly/awesome-blog/pull/677)
at `ff5c534034a11dc50cb18316cc1758df0a03267f`. Its landed tree matches the reviewed
PR tree; [main CI](https://github.com/jsolly/awesome-blog/actions/runs/37048700608)
reused that tree's successful validation. The CMS rehearsal, frozen final-source
reconciliation and independent durable backup recovery are complete. Canonical
DNS, HTTPS and the complete public-content audit passed. The repository is now
`jsolly/awesome-blog`. The renamed-repository Git production release at
`2293c3d4197010235a0af620bb4ce0661332493c` passed
[automatic Production smoke](https://github.com/jsolly/awesome-blog/actions/runs/37078297297),
and the post-rename hosted CMS rehearsal passed. John accepted the cutover and
closed the initial rollback window on October 2, 2026. Publishing may resume through
PagesCMS editorial branches and PRs. Heroku automatic deploys remain disabled;
release v315, its database/media and all backups remain retained until separately
authorized retirement.

## Architecture decisions

John chose a static public blog, retiring reader accounts, comments, AI endpoints
and the server status dashboard. Astro generates pages, Svelte handles browser
interaction, and PagesCMS edits GitHub content. No application database or
request-time backend is required. John chose editorial branches, PRs, required CI
and checked merges for publishing.

Markdown with YAML frontmatter is canonical. PagesCMS uses a source code editor,
which preserves complex imported HTML rather than roundtripping it through a
visual editor. CommonMark prose/headings are converted; tables, styled blocks,
formatted code, complex lists and embeds retain HTML. Smart punctuation and GFM
autolinking are disabled because they altered literal text and imported links.
New prose can use ordinary Markdown. Article scripts/MDX are not enabled.
See [publishing instructions](publishing.md).

Ordinary new images upload into `public/media` through PagesCMS. Large objects
are uploaded separately into existing S3 and linked by CloudFront URL. Existing
AWS media URLs remain. There is no integrated S3 uploader. A separate recovery bucket is defined through
CloudFormation; no request-time AWS service is needed.
Neither PagesCMS nor the frontend needs AWS credentials for public media.

## Source and verification

The read-only Heroku export on October 2, 2026 supplied 106 published articles,
six categories, 379 related scores and two historical aliases. It includes no
users or comments. Source IDs, author identity, timestamps, excerpts, descriptions,
image metadata, slug case and ranked related associations are retained for the
105 unchanged articles. One user-authorized recipe rewrite keeps its URL,
publication, authorship, category, legacy identity and ranked associations. The receipt at
`src/content/migration-receipt.json` records source SHA-256 and stable URLs.

John confirmed publishing frozen on October 2, 2026. The final private source is
`.migration-work/final-2026-10-02T1742Z/source-final.json`; all 496 exported records
match the earlier snapshot semantically. Its raw-file digest is recorded in
`src/content/migration-receipt.json`. The earlier snapshot is retained too. This ignored
local evidence is not an independent production backup. Git history preserves
legacy code; ignored SQLite, media, virtualenv and exports were retained.
Tracked server apps/tests/migrations, requirements, Heroku entrypoints,
CKEditor/HTMX/chart assets, AI embeddings, obsolete Linode backup scripts and
Python tooling were removed. Node tooling, CI, Dependabot and active docs replaced
their consumers together. No production resource or data was deleted.

Commands run from `/Users/johnsolly/code/awesome-blog`.

```bash
npm ci
npx --no-install playwright install chromium
npm run gate
npm run verify:migration -- .migration-work/final-2026-10-02T1742Z/source-final.json
npm run preview
```

The app gate checks types, builds, validates content/routes/feeds/CSP and creates a
real draft to prove its content and slug are absent from every output and route.
Identical duplicate post/category files must fail a real build; the checks restore
the public build after their temporary fixtures.
The full gate also checks repository/security tooling and smoke contracts. Public
preview is <http://127.0.0.1:4321>; no login or app secrets are required.

The migration oracle reads raw source HTML independently of the app renderer or
converter. It checks actual built article text, ordered links, images, iframe
attributes, heading levels/fragments, nested lists, quotes/emphasis, exact
preformatted code, table spans and inline styles, plus independently derived related
associations and RSS/Atom canonical identities. The only permitted transforms
are verified legacy heading IDs, media URL resolution, accessible iframe titles,
and removal of the inventoried recipe stylesheet after migrating its layout to
bundled CSS. Unknown scripts/styles fail reconciliation. The everyday gate permits
future edits; source parity is a migration/cutover check, not a content freeze.

The recipe article is an explicit exception in
`src/content/intentional-rewrites.json`. SHA-256 hashes pin its original raw legacy
record and complete replacement post. The oracle rejects later changes to either,
checks preserved identity fields, and derives feed expectations from the reviewed
replacement metadata. Built-output contracts verify all twelve no-JavaScript
recipes, TRN tables, first-party images and assistant downloads. The remaining
105 articles retain their independent raw-source checks. See [recipe maintenance](recipes.md).

Public URLs remain `/`, `/all-posts/`, `/search/?searched=...`, existing posts
and categories, `/rss/`, `/atom/`, `/sitemap.xml`, `/privacy/`,
`/works-cited/` and security resources. Search/query pagination requires JavaScript;
the archive lists every published article without it. Drafts are excluded from
routes, search, feeds, sitemap and client props. Heading links, print and related
posts remain. The static build sanitizes HTML and emits hashed script CSP.

Historical aliases are in `src/content/redirects.json` and `vercel.json`. The
closed-loop alias already ended at a missing article on the old production site,
verified October 2. Its recorded destination remains; no new article was invented.
The favorite-podcasts alias still targets its existing published article.
Vercel enforces Astro's trailing slash URLs, including normalized alias sources
and destinations. Bare article URLs redirect to their canonical directory route.
The production smoke checks the readable alias and both feed URL forms; the full
cutover audit separately verifies the documented missing target remains a 404.

## Required CMS rehearsal

Use the [PagesCMS GitHub App](https://app.pagescms.org) to access
`jsolly/awesome-blog`. Prefer repository-scoped access for a new installation;
do not alter unrelated access on an existing installation. For the initial rehearsal, select a separate
editorial branch based on the reviewed migration head, where `.pages.yml` exists.
After cutover, start editorial branches from current main. Never weaken
protected-main policy. Authentication, isolated branch creation, editor access and a
code/table/frame article saves and reopens, category creation, media upload and
draft-to-published output are verified. The isolated
[rehearsal PR #679](https://github.com/jsolly/awesome-blog/pull/679) passed
the actual required `CI / ci` check and closed without merging its fixtures.
Initial inspection found
that date fields reinitialized legacy ISO timestamps and image fields treated
CloudFront URLs as GitHub paths. Timestamps now use validated ISO strings; cover
images use a URL/media-path string with uploads through the Media sidebar.
Hosted saves emit unquoted YAML timestamps and may omit empty optional fields.
The post loader and migration tools parse YAML 1.2 before validating metadata;
the build preserves timestamp source strings and applies declared empty defaults.
The code-article roundtrip retained six fractional digits, timezone offsets,
remote image URLs, its full body and unmanaged legacy keys.
The table and embedded-frame articles retained their exact bodies and meaningful
metadata after hosted saves; original titles were restored afterward.

After the repository rename, the hosted CMS saved and reopened an isolated draft,
then published it on the rehearsal branch. The roundtrip preserved the body,
code, image URL, unmanaged legacy keys and the timestamp
`2026-10-02T19:40:23.123456-04:00`, apart from a terminal blank line in the body.
Draft exclusion and published article/category/archive/search/feed/sitemap output
passed, as did desktop and mobile reading. Literal GFM table syntax remains literal
under the declared CommonMark policy. [Rehearsal PR #685](https://github.com/jsolly/awesome-blog/pull/685)
passed [CI](https://github.com/jsolly/awesome-blog/actions/runs/37079129740) and closed
without merging; its fixture is absent from `main` and production. Automatic branch
previews remained disabled.

1. Save and reopen existing table, code and iframe posts. Compare the source diff,
   metadata, timestamps, media URLs and unmanaged legacy keys. Confirm source body
   editing does not rewrite retained markup.
2. Create a category and reference it from a draft. Upload an ordinary image with
   alt text/dimensions. Verify draft exclusion with the actual CMS-authored file.
3. Rehearse a PR publish with `CI / ci`; verify article/category/image/search/feed
   output. Local preview is available; automatic branch previews are disabled.
4. Edit a published post without changing its slug and verify its original URL.

`settings.content.merge: true` retains unmanaged reconciliation metadata. If the
hosted CMS changes it anyway, stop publishing and repair the schema before cutover.

## Production cutover

The inspected Vercel team is `jsolly's projects`, ID
`team_T8yHg0aDz7nCbyBgJh5a2saR`. Project `blogthedata`, ID
`prj_QxSNy3z51xOp295HUvPfDa1JY9h8`, is connected to GitHub repository
`jsolly/awesome-blog`, repository ID `286148731`, with production branch
`main`. The persisted configuration was read back on October 2, 2026: Astro,
Node 24, `npm ci`, `npm run build`, output `dist`, project previews disabled,
and Vercel authentication on deployment URLs while custom domains remain public.
The canonical DNS cutover completed on October 2, 2026. Both Cloudflare CNAMEs
point to Vercel with DNS-only service and TTL Auto; the Google verification TXT
record is unchanged. HTTPS validates and the apex redirects to www, preserving
the requested path and query. The initial Git production deployment
`dpl_4vJESG2KYmB6KvVThp4twNKC9Yrn` served full SHA
`4e0347ba886dbe36e1e02cf85ea80a67bec78765`. Its
[canonical Production smoke](https://github.com/jsolly/awesome-blog/actions/runs/37072840179)
passed through the manual fallback. The complete live audit passed all 106
articles and their bare URLs, 13 other pages, 241 referenced assets, four feed
forms and both historical aliases in both URL forms, including the documented
pre-existing 404. Automatic smoke was skipped before the environment variable
was saved. John then saved `VERCEL_PRODUCTION_ENVIRONMENT=Production` and renamed
the same repository, ID `286148731`, to `awesome-blog`.
[Identity PR #684](https://github.com/jsolly/awesome-blog/pull/684) then landed at
`2293c3d4197010235a0af620bb4ce0661332493c`. Its Git-triggered Vercel production
deployment `dpl_DbF7JTxAMg4wwynVLVPcBqegovHu` reached READY, and GitHub deployment
`6820445317` triggered the successful
[automatic canonical Production smoke](https://github.com/jsolly/awesome-blog/actions/runs/37078297297)
for that exact SHA without fallback. The post-rename hosted CMS rehearsal above
also passed. John explicitly chose to retain Vercel's existing All repositories
GitHub App access; no permissions changed.
Heroku automatic deploys remain disabled; release v315 and its database/media
are retained. John accepted the verified cutover and closed the initial rollback
window on October 2, 2026. Publishing may resume through the new CMS workflow;
acceptance does not authorize teardown of retained resources or backups.
John explicitly authorized migration backups and admin activities on October 2,
2026. The agent can perform these steps using available authorized access.
Sign-in and any required human input use Chrome. New security-sensitive access
grants and binding terms still need approval when presented. No teardown is authorized.

1. Freeze publishing in the old application. Record the current Heroku release/version/full SHA,
   original DNS records and a successful old-host article/search check. Make an
   independent database backup and retain media outside this checkout. Heroku
   backup b002 was captured after John's freeze and restored locally on October 2.
   All exported fields across 106 posts, six categories, 379 similarity rows,
   two redirects and three sites matched the final source after matching its
   millisecond timestamp precision. The isolated cluster had no TCP listener and
   was stopped and removed; the earlier b001 recovery evidence is retained too.
   The local S3 copy contains 1,009 files, 101,335,569 bytes. These local artifacts
   match the frozen final inventory, with no added, removed or changed objects.
   John uploaded the frozen bundle to the independent backup bucket; exact-version
   retrieval, checksum/retention checks, all-media verification and database recovery
   passed. Image and PDF samples were opened from that downloaded version. The
   version and recovery receipt are recorded in [migration-backups.md](migration-backups.md).
   Record S3 bucket/object inventory,
   versioning/backup status and a recovery copy; GitHub is not a backup for S3.
2. Re-export content, categories, similarities, redirects and sites. Import into
   a new empty scratch directory and reconcile changed articles with the CMS files.
   Never overwrite CMS edits automatically. Re-run source parity and the full gate.
   Keep publishing frozen through the rollback window.
3. Disable Heroku automatic deploys for `blogthedata` in its GitHub deployment
   settings, retaining the serving release/database. Record the setting before
   allowing `/ship` to merge this runtime replacement after green `CI / ci`.
4. Connect `jsolly/awesome-blog` to the existing Vercel project after the
   reviewed Astro replacement lands on `main`. Use Astro, production branch
   `main`, Node 24, install `npm ci`, build `npm run build`, output `dist`.
   Confirm `vercel.json` suppresses all other Git refs. Keep protected main and
   Vercel deployment protection intact; do not add runtime AWS secrets.
5. Verify the project-domain deployment and full SHA at `/release.json`, public
   reading, GET search, categories, feeds and both viewports. Confirm RSS MIME
   `application/rss+xml` and Atom `application/atom+xml`. Astro's static preview
   omits endpoint MIME headers, so Vercel's committed MIME rules require this real
   deployment check. Record deployment URL/SHA and actual GitHub production
   deployment creator/environment. The smoke automatic trigger expects the Vercel
   App creator `vercel[bot]`; correct it only from observed event evidence.
6. Add `www.blogthedata.com` and the apex domain to Vercel. Apply the DNS records
   Vercel actually supplies, recording original/new values. Do not invent CNAME/A
   records. The committed apex redirect preserves the canonical www host.
7. Set the GitHub repository variable `VERCEL_PRODUCTION_ENVIRONMENT` to the
   verified production event environment. Only successful Vercel events trigger
   smoke; Heroku events cannot prove this release. Follow that exact SHA's canonical
   smoke to success. If automatic delivery is absent, dispatch `Production smoke`
   on `main` with the full deployed SHA and a unique UUID request ID. Record its
   run URL, release SHA and deployment URL. A skipped/stale/missing/failed run is
   incomplete. Verify every existing article URL and media after cutover.
8. After verifying the cutover, rename the GitHub repository to `awesome-blog`
   and move the local checkout to `/Users/johnsolly/code/awesome-blog`. Update origin,
   PagesCMS, Vercel Git linkage, CI ownership checks and documentation. Recheck
   publishing and production against the renamed repository. Preserve existing
   article text and URLs containing old technology names. Remove all remaining
   framework references from active tooling and documentation.
9. End the freeze only after the checks pass and John closes the initial rollback
   window. Retain Heroku/database/S3/CloudFront/IAM until separately authorized
   retirement. No teardown commands are included in this migration.

These Heroku commands are cwd-independent. Backup capture/download are authorized
migration admin operations. Use a fresh destination to preserve earlier receipts.
The export is read-only.

```bash
npx --yes heroku@11.10.0 releases -a blogthedata --num 5
npx --yes heroku@11.10.0 pg:backups:capture -a blogthedata
npx --yes heroku@11.10.0 pg:backups:download -a blogthedata --output /private/tmp/blogthedata-before-astro.dump
npx --yes heroku@11.10.0 run --no-tty -a blogthedata -- python manage.py dumpdata blog.category blog.post blog.similarity redirects.redirect sites.site --indent 2 > /private/tmp/blogthedata-final-export.json
```

Move the DB/media backups to durable independent storage and record their receipt
before cutover. Domain records are unavailable until the domains are added;
use Vercel's actual supplied records rather than guessed commands.
The private S3 configuration and creation history are in
[migration-backups.md](migration-backups.md). The CloudFormation stack is created
and verified. The frozen recovery bundle is uploaded; recovery from its exact S3
version has passed the required database and media checks.

For the media backup, use your existing authorized AWS profile and confirm
`aws sts get-caller-identity` reports account `730335616323`. The commands below
download current objects only and do not modify S3. Run them during the publishing
freeze, from `/Users/johnsolly/code/awesome-blog`, into new destinations.
[AWS sync](https://docs.aws.amazon.com/cli/latest/reference/s3/sync.html) downloads
objects; [the inventory command](https://docs.aws.amazon.com/cli/latest/reference/s3api/list-objects-v2.html)
uses the CLI's default pagination. Do not add `--no-paginate` or `--max-items`.

```bash
aws sts get-caller-identity
aws s3api get-bucket-versioning --bucket blogthedata > /private/tmp/blogthedata-versioning-before-astro.json
aws s3api list-objects-v2 --bucket blogthedata > /private/tmp/blogthedata-objects-before-astro.json
aws s3api list-object-versions --bucket blogthedata > /private/tmp/blogthedata-versions-before-astro.json
aws s3 sync s3://blogthedata /private/tmp/blogthedata-media-before-astro --checksum-mode ENABLED --only-show-errors
node scripts/verify-media-backup.mjs /private/tmp/blogthedata-objects-before-astro.json /private/tmp/blogthedata-media-before-astro /private/tmp/blogthedata-media-backup-receipt.json
aws s3 sync s3://blogthedata /private/tmp/blogthedata-media-before-astro --dryrun
```

The verifier requires every current inventory object to exist at its recorded
size and records local SHA-256 checksums using streaming reads. AWS validates
stored checksums when available; local hashes do not independently prove a match
to an object with no stored checksum. The final dry run must propose no downloads.
Open sample image/PDF/code media from the copy and record those checks. Store the
copy, inventory, versioning/versions output, checksum receipt and database dump in
independent durable storage, with location and retrieval proof in the release
receipt. This copies current objects, not old versions; if historical restoration
is required, capture those versions separately before permitting cutover. No live
versioning, retention or IAM settings are changed by this procedure.

## Release proof and rollback

`/release.json` embeds the full build commit SHA. Production smoke waits until the
canonical site serves that exact SHA, then checks article reading, GET search,
RSS/Atom MIME and mobile navigation. It uses only public GETs and browser reads.
Receipts, traces and screenshots upload even on failure. The canonical manual
[Production smoke](https://github.com/jsolly/awesome-blog/actions/runs/37072840179)
passed for the initial Vercel cutover release. The renamed-repository Git release
recorded above passed [automatic Production smoke](https://github.com/jsolly/awesome-blog/actions/runs/37078297297),
and hosted CMS verification passed in rehearsal PR #685. John accepted these checks
and closed the initial rollback window on October 2, 2026.

Publishing may now resume. Before any rollback to the old application, reconcile
Git-authored changes made after the frozen export back into the retained application.
Restore the recorded original DNS routing to the retained Heroku release, then
verify canonical reading/search. Keep deployment receipts for diagnosis. Retain
Heroku, its database/media and independent backups until separately authorized
retirement; migration acceptance does not authorize deleting production resources.
