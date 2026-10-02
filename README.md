# Blogthedata

A static technical blog built with Astro and Svelte. Markdown articles and category
metadata live in GitHub and are edited with PagesCMS. Vercel builds production from
protected `main`; ordinary images live in the repository and existing large media
remains on AWS S3/CloudFront.

The migration is implemented locally. Production still runs Django on Heroku until
the [cutover runbook](docs/astro-migration.md) is completed. Do not merge the runtime
replacement before disabling Heroku automatic deploys.

## Develop

Use Node 24 (`.nvmrc`), npm, and Bash 5 for repository scripts. Commands run from
`/Users/johnsolly/code/awesome-django-blog`.

```bash
npm ci
npx --no-install playwright install chromium
npm run gate:app
npm run dev
```

The local site is <http://127.0.0.1:4321>. `npm run build` writes `dist/`;
`npm run preview` serves that build. No application secrets, database or cloud
credentials are required. `npm run worktree:init` installs pinned Node dependencies
in a fresh checkout. The full `npm run gate` also runs the shared dotagents security
and repository checks; see [AGENTS.md](AGENTS.md).

## Content and behavior

Posts are `src/content/posts/*.md` with YAML frontmatter. Categories are JSON files
in `src/content/categories`. `.pages.yml` supplies typed metadata and a Markdown
source editor. CommonMark prose and headings are converted from the old HTML;
complex tables, code, styled blocks and embeds retain HTML to preserve authored
meaning. No MDX or executable article scripts are enabled. Rendering sanitizes HTML.

The site provides article reading, category pages, a complete archive, GET search,
pagination, RSS/Atom feeds, sitemap, heading links and print controls. Search and
pagination use Svelte in the browser; the archive remains readable without
JavaScript. Drafts are excluded from every public output. Reader accounts, comments,
AI endpoints and the status dashboard were retired with the static migration.

## Publish

Install the PagesCMS GitHub App for this repository, then edit an editorial branch
created from current `main`. Save changes, open a PR, pass `CI / ci`, and merge
through the existing review process. Vercel deploys `main` only; automatic branch
previews are disabled. See [publishing instructions](docs/publishing.md) and the
[deployment/cutover runbook](docs/astro-migration.md).

New images upload into `public/media`. Large objects are uploaded separately to S3
and linked with their CloudFront URL; the CMS has no AWS credentials or S3 uploader.
Retain stable post and category slugs, including case, when editing existing content.

See [contributing](docs/CONTRIBUTING.md), [security](docs/SECURITY.md), and
[license](LICENSE).
