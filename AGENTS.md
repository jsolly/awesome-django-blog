# AGENTS.md

## Stack

Django 5.2 blogging platform on Python 3.14. SQLite by default, Postgres optional. HTMX for partial updates, CKEditor 5 for authoring, OpenAI for chatbot/title generation. WhiteNoise + optional S3/CloudFront for static/media. Deploys via Procfile (Heroku-style).

## Common Commands

All commands run from the repo root with `.venv` activated.

```bash
# First-time setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py setup_env          # creates .env.local from .env.example with a fresh SECRET_KEY
python manage.py migrate
python manage.py runserver

# Tests (pytest, uses tests/base.py SetUp class)
pytest tests                        # full suite
pytest tests/test_views.py          # single file
pytest tests/test_views.py::PostDetailViewTests::test_post_detail_view_uses_correct_template  # single test

# Coverage
coverage run --rcfile=config/.coveragerc -m pytest tests
coverage report -m --skip-covered --rcfile=config/.coveragerc

# Lint / format (ruff config is in config/pyproject.toml, NOT root)
ruff check --config ./config/pyproject.toml app
ruff format app

# Git hooks — pre-push gate (tracked in .git-hooks/, configured like the rest of the fleet)
git config core.hooksPath .git-hooks

# Worktree provisioning — run once after EnterWorktree / `git worktree add`
npm run worktree:init               # creates .venv + installs pinned deps (fast on a warm pip cache)
# A fresh worktree carries no gitignored state → no local sqlite DB and no collected
# static manifest. The pre-push gate builds both itself (it runs collectstatic + migrate
# before pytest), so `git push` is fine after worktree:init alone. But to run the tests
# or any manage.py command MANUALLY first, build them once — otherwise pytest fails with
# "no such table" / "Missing staticfiles manifest entry" (DEBUG=False uses
# ManifestStaticFilesStorage, which requires a collectstatic manifest):
USE_SQLITE=true python manage.py migrate --noinput   # build the local .sqlite schema
python manage.py collectstatic --noinput             # build the static manifest

# Seed data — for manual `runserver` browsing ONLY. The test suite does NOT need it:
# tests/base.py self-seeds (creates admin/comment_only/uncategorized + per-test fixtures).
python manage.py import_posts utilities/seed_posts/posts.json

# Recompute post-similarity embeddings (writes blog/df.pkl)
python manage.py recalculate_post_simularities

# Live reload (optional, set LIVERELOAD=True in .env.local, run in second terminal)
python manage.py livereload
```

Default seeded accounts: `admin/admin` and `comment_only/comment_only`. For browser smoke / admin login, use `DEFAULT_USER` / `DEFAULT_PASSWORD` from `.env.local` (see `.env.example`; keep in sync with the seed).

## Architecture

Three Django apps plus a project package:

- **`app/`** — project config. Single-module `settings.py` (not a package; `DJANGO_SETTINGS_MODULE=app.settings`). Contains URL root, ASGI/WSGI, custom `WwwRedirectMiddleware`, `storage_backends.py` (S3 variants for public/private/post-image/static), and `sitemaps.py`.
- **`blog/`** — domain core. Models: `Category`, `Post` (CKEditor5 content, ResizedImageField → WEBP), `Comment`. Class-based views in `views.py` cover CRUD, search, status page, and two GPT endpoints (`generate-with-gpt`, `answer-with-gpt`). Post-similarity uses a pickled DataFrame at `blog/df.pkl` produced by the `recalculate_post_simularities` management command — don't regenerate casually.
- **`users/`** — auth views, profile, password reset. Wraps Django's built-in auth views with custom templates.
- **`tests/`** — flat pytest suite at repo root (NOT inside each app). All test classes inherit from `tests.base.SetUp`, which forces `USE_SQLITE=True` / `USE_CLOUD=False` at import time and pre-creates `admin`, `comment_only`, default `uncategorized` category, and a `first_post`/`first_comment`. Use `tests/utils.py` (`create_unique_post`, `create_comment`) instead of building fixtures inline. The `tearDown` deletes all `Post` rows between tests — **treat each test as starting from zero `Post` rows**; rebuild fixtures via `tests/utils.py`.

Key cross-cutting pieces:

- **CSP** is enforced via `django-csp` (`CSP_*` settings in `app/settings.py`). Adding any new external script/style/font/image source requires updating these tuples or it'll be blocked at runtime — symptom is silent breakage in the browser console, not a Django error. `livereload` injects its own CSP entries, gated on `LIVERELOAD=True`.
- **HTML minification** runs on every response via `django-htmlmin` middleware. Disable in dev settings when debugging template whitespace.
- **Storage** flips entirely on `USE_CLOUD`. With `USE_CLOUD=True`, default/media/static/CKEditor uploads all route through `app/storage_backends.py` to S3; otherwise FileSystemStorage + WhiteNoise. Tests force `USE_CLOUD=False` regardless of `.env.local`.
- **CKEditor 5 image uploads** require `CSRF_COOKIE_HTTPONLY = False`. The setting stays commented out in `app/settings.py` until image upload is actively needed.
- **Status page** (`/status/`) is cached for 60s via `cache_page` in `LocMemCache` (per-process — assumes single-instance deploy; tests can see stale cache).
- **GPT chatbot** loads `blog/df.pkl` (post embeddings) into memory. Files in `utilities/create_embeddings/` build it; the management command refreshes it.

## Deploy & operations

Heroku CLI is a devDependency of this repo (`package.json`; run `npm install` once, Node 24 per `.nvmrc`) — invoke it via `npx heroku` rather than reaching for the dashboard. App is **`blogthedata`** in the `Personal` team. Auth: `npx heroku login` (browser flow).

```bash
npx heroku releases -a blogthedata --num 5     # last 5 deploys
npx heroku logs -a blogthedata --num 200       # recent dyno logs
npx heroku ps -a blogthedata                   # dyno status
```

The gate (`.git-hooks/pre-commit`) must run against the pinned project deps, never system Python, so it needs a `.venv` (and the pinned `markdownlint-cli2` from `node_modules` for the markdown sub-gate). A fresh git worktree branches from `origin/main` and carries no gitignored files, so it starts without either. Two paths cover that without a manual install of the heavy scientific stack (numpy/scipy/scikit-learn/pandas/matplotlib): for a **code-only** change the gate transparently **borrows the main checkout's `.venv` and `node_modules`** (resolved via the shared git common dir) when the worktree's `requirements.txt` / `package-lock.json` are byte-identical to the main checkout's — zero setup, fully offline. If you **changed those deps** in the worktree the borrowed copy would be stale, so the gate refuses and tells you to run **`npm run worktree:init`**, which builds the worktree its own `.venv` + `node_modules` (fast on warm pip/npm caches). System Python is never used either way.

Deploy is **automatic from GitHub `main`**: Heroku is connected to the GitHub repo with automatic deploys, so **merging a PR (or any push to `main`) triggers a production build** — there is no local deploy command and no push URL to `git.heroku.com` (the old "Heroku Git" dual-push-URL model is dead; don't re-add push URLs to `.git/config`). The pre-commit hook runs the lint/test gate only; GitHub Actions CI is the backstop. No Heroku-side build customization, Procfile + buildpacks only.

**Agents: never merge PRs on this repo.** Because merge = prod deploy (Heroku attribution), the human merges after reviewing. Open the PR, report it, and stop — do not run `gh pr merge` in any form. Validate locally via the worktree + pre-commit gate before opening the PR; verify a deploy landed with `npx heroku releases` after the human merges.

**S3 access** (django-storages → S3 + CloudFront, gated on `USE_CLOUD=True`): the Heroku dyno authenticates via a long-lived static IAM key set as Heroku config vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`). The IAM user is **`awesome-django-blog-heroku`** with a single bucket-scoped inline policy `awesome-django-blog-s3-access` — `s3:Get/Put/Delete/ListBucket/ACL` on `arn:aws:s3:::blogthedata` only. **Don't widen.** Heroku doesn't issue OIDC tokens to dynos ([heroku/roadmap#247](https://github.com/heroku/roadmap/issues/247)), so the long-lived key is unavoidable; the narrow policy is the mitigation. AWS console/CLI: use credentials for account `730335616323` via local `AWS_PROFILE` — do not commit profile names in this repo.

## Conventions

- Ruff config (`config/pyproject.toml`) ignores `E402`, `E501`, `F403` and excludes `apps.py` / `*/settings/*` — these accommodate Django star-imports, top-of-file `setup()` calls in tests, and intentional long lines.
- Test convention: flat `tests/test_<module>.py` mirroring the source module, classes inheriting `SetUp` from `tests/base.py`.
- Conventional Commits (`feat(blog): …`, `fix(users): …`).

## Local UI verification

Auth-gated admin/authoring UI (public blog pages need no login). Follow `rules/frontend-verification.md` (fleet smoke: desktop + mobile screenshots, console clean).

- **Dev server:** with `.venv` activated — `python manage.py runserver` → <http://127.0.0.1:8000>
- **Sign-in:** Django auth with `DEFAULT_USER` and `DEFAULT_PASSWORD` from `.env.local` (see `.env.example`). Keep these in sync with seeded accounts (local defaults: `admin` / `admin` after seed/setup).
- **Do not** invent credentials or commit `.env.local`.
