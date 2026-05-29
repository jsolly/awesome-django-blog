# AGENTS.md

@.agents/AGENTS.md

## Cursor Cloud

Cloud agents: see `docs/cloud-agents.md` (fleet layout, subtree updates). After the first successful cloud boot, pin the VM snapshot per **Snapshot bootstrap (agent-run)** in that doc (`./scripts/pin-cloud-snapshot.sh`).

## Stack

Django 5.1 blogging platform on Python 3.13. SQLite by default, Postgres optional. HTMX for partial updates, CKEditor 5 for authoring, OpenAI for chatbot/title generation. WhiteNoise + optional S3/CloudFront for static/media. Deploys via Procfile (Heroku-style).

## Common Commands

All commands run from the repo root with `.venv` activated.

```bash
# First-time setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py setup_env          # creates .env from .env.example with a fresh SECRET_KEY
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

# Pre-commit hooks (configured under config/, not root)
cd config && pre-commit install

# Seed data — required for many tests since base.py expects existing admin/comment_only users + "uncategorized" category
python manage.py import_posts utilities/seed_posts/posts.json

# Recompute post-similarity embeddings (writes blog/df.pkl)
python manage.py recalculate_post_simularities

# Live reload (optional, set LIVERELOAD=True in .env, run in second terminal)
python manage.py livereload
```

Default seeded accounts: `admin/admin` and `comment_only/comment_only`.

## Architecture

Three Django apps plus a project package:

- **`app/`** — project config. Single-module `settings.py` (not a package; `DJANGO_SETTINGS_MODULE=app.settings`). Contains URL root, ASGI/WSGI, custom `WwwRedirectMiddleware`, `storage_backends.py` (S3 variants for public/private/post-image/static), and `sitemaps.py`.
- **`blog/`** — domain core. Models: `Category`, `Post` (CKEditor5 content, ResizedImageField → WEBP), `Comment`. Class-based views in `views.py` cover CRUD, search, status page, and two GPT endpoints (`generate-with-gpt`, `answer-with-gpt`). Post-similarity uses a pickled DataFrame at `blog/df.pkl` produced by the `recalculate_post_simularities` management command — don't regenerate casually.
- **`users/`** — auth views, profile, password reset. Wraps Django's built-in auth views with custom templates.
- **`tests/`** — flat pytest suite at repo root (NOT inside each app). All test classes inherit from `tests.base.SetUp`, which forces `USE_SQLITE=True` / `USE_CLOUD=False` at import time and pre-creates `admin`, `comment_only`, default `uncategorized` category, and a `first_post`/`first_comment`. Use `tests/utils.py` (`create_unique_post`, `create_comment`) instead of building fixtures inline. The `tearDown` deletes all `Post` rows between tests — **treat each test as starting from zero `Post` rows**; rebuild fixtures via `tests/utils.py`.

Key cross-cutting pieces:

- **CSP** is enforced via `django-csp` (`CSP_*` settings in `app/settings.py`). Adding any new external script/style/font/image source requires updating these tuples or it'll be blocked at runtime — symptom is silent breakage in the browser console, not a Django error. `livereload` injects its own CSP entries, gated on `LIVERELOAD=True`.
- **HTML minification** runs on every response via `django-htmlmin` middleware. Disable in dev settings when debugging template whitespace.
- **Storage** flips entirely on `USE_CLOUD`. With `USE_CLOUD=True`, default/media/static/CKEditor uploads all route through `app/storage_backends.py` to S3; otherwise FileSystemStorage + WhiteNoise. Tests force `USE_CLOUD=False` regardless of `.env`.
- **CKEditor 5 image uploads** require `CSRF_COOKIE_HTTPONLY = False`. The setting stays commented out in `app/settings.py` until image upload is actively needed.
- **Status page** (`/status/`) is cached for 60s via `cache_page` in `LocMemCache` (per-process — assumes single-instance deploy; tests can see stale cache).
- **GPT chatbot** loads `blog/df.pkl` (post embeddings) into memory. Files in `utilities/create_embeddings/` build it; the management command refreshes it.

## Deploy & operations

Heroku CLI (`heroku`) is installed locally — use it directly rather than reaching for the dashboard. App is **`blogthedata`** in the `Personal` team. Auth: `heroku login` (browser flow).

```bash
heroku releases -a blogthedata --num 5     # last 5 deploys
heroku logs -a blogthedata --num 200       # recent dyno logs
heroku ps -a blogthedata                   # dyno status
```

Auto-deploys from GitHub `master` after the `build` status check passes — no Heroku-side build customization, Procfile + buildpacks only.

**S3 access** (django-storages → S3 + CloudFront, gated on `USE_CLOUD=True`): the Heroku dyno authenticates via a long-lived static IAM key set as Heroku config vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`). The IAM user is **`awesome-django-blog-heroku`** with a single bucket-scoped inline policy `awesome-django-blog-s3-access` — `s3:Get/Put/Delete/ListBucket/ACL` on `arn:aws:s3:::blogthedata` only. **Don't widen.** Heroku doesn't issue OIDC tokens to dynos ([heroku/roadmap#247](https://github.com/heroku/roadmap/issues/247)), so the long-lived key is unavoidable; the narrow policy is the mitigation. AWS console/CLI: use credentials for account `730335616323` via local `AWS_PROFILE` (see `~/.agents/rules/aws.md`) — do not commit profile names in this repo.

## Conventions

- Ruff config (`config/pyproject.toml`) ignores `E402`, `E501`, `F403` and excludes `apps.py` / `*/settings/*` — these accommodate Django star-imports, top-of-file `setup()` calls in tests, and intentional long lines.
- Test convention: flat `tests/test_<module>.py` mirroring the source module, classes inheriting `SetUp` from `tests/base.py`.
- Conventional Commits (`feat(blog): …`, `fix(users): …`).
