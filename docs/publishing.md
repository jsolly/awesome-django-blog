# Publishing with PagesCMS

Use [hosted PagesCMS](https://app.pagescms.org) after granting its GitHub App access
only to `jsolly/awesome-django-blog`. Choose an editorial branch made from current
`main`. Saves create commits on that branch; production changes only after a PR
passes `CI / ci` and merges. Start each subsequent branch from updated `main`.
Do not edit protected `main` directly or weaken branch protection.

## Write an article

Create a post with a stable slug, title, description, category, publication/update
timestamps, and an image with alt text. New posts default to drafts. The source
editor accepts CommonMark: paragraphs, headings, explicit links, lists, emphasis
and fenced code. Use ordinary Markdown for new prose. Complex tables and embeds
can use HTML; scripts, event handlers and unapproved iframe providers are removed.
GFM automatic linking/tables and typographic rewriting are disabled, so write
links explicitly and use HTML for tables. Imported HTML blocks retain formatting.
The card excerpt is optional HTML; absent excerpts use the SEO description.

Only YouTube, YouTube No-Cookie, diagrams.net and nbviewer frames are supported.
Any additional provider needs a reviewed renderer/CSP change. Assets cannot load
runtime CSS/JS from third-party CDNs. Preserve existing heading text if its linked
fragment must stay stable; H1–H3 fragments follow the former blog's algorithm.

Upload ordinary images through the CMS to `public/media`. Resize/compress before
uploading. Put large downloads, videos or datasets in existing S3 separately and
link their CloudFront URLs. The CMS does not upload to S3. Never paste AWS credentials
into article metadata or CMS fields.

Update `updated` when editing a post. Keep published slugs and their case unchanged.
Category slugs are equally stable. Choose up to three related posts manually; there
is no embedding service. Unmanaged legacy IDs/image paths remain for reconciliation.

## Review and publish

Check the PR diff for accidental frontmatter/body rewrites. Run the Node app gate
and preview the build locally. New drafts must be absent from routes, archive,
search, feeds, sitemap and client data; the gate exercises a real sentinel draft.
Set `draft` to false only when ready. Review image accessibility, canonical URL,
category, article reading, search and feed entries, then merge after green CI.
Automatic branch previews are disabled; use local preview unless John explicitly
authorizes the fleet's opt-in preview workflow.

Before first production cutover, rehearse save/reopen of existing table/code/frame
articles, new category/image/draft, and a PR publish. Hosted CMS authentication and
its actual save behavior have not been verified by the local implementation.

## Content validation

Article-specific Markdown lint allows retained HTML, original punctuation, heading
order and verbatim code whitespace. These are authored content, not repository
style errors. Astro schemas, route/feed/draft contracts and migration semantic
parity supply the structural checks. Engineering docs retain normal Markdown lint.
Changes to imported source are checked against a fresh export only during cutover;
the everyday gate permits legitimate future edits and new feed entries.
