# AGENTS.md

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
- **HTML minification** via `django-htmlmin` middleware runs on every response — beware when debugging template whitespace issues.
- **Storage** flips entirely on `USE_CLOUD`. With `USE_CLOUD=True`, default/media/static/CKEditor uploads all route through `app/storage_backends.py` to S3; otherwise FileSystemStorage + WhiteNoise. Tests force `USE_CLOUD=False` regardless of `.env`.
- **CKEditor 5 image uploads** require `CSRF_COOKIE_HTTPONLY = False` (commented out in settings with a note). Keep it off.
- **Status page** (`/status/`) is cached for 60s via `cache_page`; the project uses `LocMemCache` so cache is per-process — fine for single-dyno Heroku, surprising in tests.
- **GPT chatbot** loads `blog/df.pkl` (post embeddings) into memory. Files in `utilities/create_embeddings/` build it; the management command refreshes it.

## Conventions

- Ruff config (`config/pyproject.toml`) ignores `E402`, `E501`, `F403` and excludes `apps.py` / `*/settings/*`. Leave them ignored — these handle Django star-imports, top-of-file `setup()` calls in tests, and intentional long lines.
- Test convention: flat `tests/test_<module>.py` mirroring the source module, classes inheriting `SetUp` from `tests/base.py`.
- Conventional Commits (`feat(blog): …`, `fix(users): …`).
- CI's test step is currently commented out in `.github/workflows/django-test-deploy-master.yaml`. Run tests locally before pushing.
