#!/usr/bin/env bash
# Pre-push gate for awesome-django-blog (Python/Django).
#
# Invoked by .git-hooks/pre-push (core.hooksPath=.git-hooks). Replaces the
# `build` job of the old .github/workflows/django-test-deploy-master.yaml: the
# lint + test gate now runs locally on push to master. CodeQL was dropped.
#
# Deploy is no longer a GitHub integration: the Heroku deploy method is now
# "Heroku Git", and the `origin` remote carries a second push URL pointing at
# git.heroku.com/blogthedata. A single `git push origin master` therefore fans
# out to both GitHub and Heroku (Heroku builds on the master push). This hook
# only GATES that push — it does not itself run any deploy command, so there is
# no nested `git push` and nothing to recurse into. See AGENTS.md for the
# one-time `git remote set-url --add --push` setup.
#
# Only acts on a non-deleting push to main/master; feature-branch pushes stay
# fast. Escape hatch: FLEET_SKIP_PREPUSH=1 git push.
set -euo pipefail

if [ "${FLEET_SKIP_PREPUSH:-}" = "1" ]; then
  echo "⚠ FLEET_SKIP_PREPUSH=1 — skipping pre-push gate" >&2
  exit 0
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# pre-push stdin: <local ref> <local sha> <remote ref> <remote sha>
ZERO="0000000000000000000000000000000000000000"
push_to_main=""
LOCAL_SHA="" REMOTE_SHA=""
while read -r _local_ref local_sha remote_ref remote_sha; do
  case "$remote_ref" in
    refs/heads/main | refs/heads/master)
      [ "$local_sha" = "$ZERO" ] && continue
      push_to_main="$remote_ref"
      LOCAL_SHA="$local_sha"
      REMOTE_SHA="$remote_sha"
      ;;
  esac
done
[ -z "$push_to_main" ] && exit 0

# --- Markdown lint -----------------------------------------------------------
# Run whenever the pushed range touches markdown, BEFORE the docs-only fast path
# below, so docs-only (and mixed) pushes always lint their markdown and then the
# fast path still skips the expensive gate + deploy. Cheap. Fail-safe: lint when
# the range cannot be computed.
prepush_md_changed() { # <remote_sha> <local_sha>
  local remote_sha="$1" local_sha="$2" f
  [ -n "$remote_sha" ] && [ "$remote_sha" != "$ZERO" ] || return 0
  git cat-file -e "$remote_sha" 2>/dev/null || return 0
  git merge-base --is-ancestor "$remote_sha" "$local_sha" 2>/dev/null || return 0
  while IFS= read -r f; do
    case "$f" in *.md | *.mdx | *.markdown) return 0 ;; esac
  done < <(git diff --name-only "$remote_sha" "$local_sha")
  return 1
}
if prepush_md_changed "$REMOTE_SHA" "$LOCAL_SHA"; then
  echo "• markdown lint"
  bash "$ROOT/scripts/lint-md.sh"
fi

# --- Doc-only fast path -------------------------------------------------------
# Skip the full gate when the pushed range touches only documentation, so prose
# edits don't pay for the lint/type/test battery. Conservative allow-list:
# root-level *.md, the docs/ tree, .github/*.md, and LICENSE — markdown that is
# site CONTENT (under src/, content/, …) still runs the full gate. Falls back to
# the full gate whenever the range can't be computed (new branch, non-fast-
# forward, missing remote sha), so it can only skip too little, never too much.
# Force the full gate with:  FLEET_DOC_FAST=0 git push
prepush_doc_only() { # <remote_sha> <local_sha>  → 0 when the fast path applies
  local remote_sha="$1" local_sha="$2" files f
  [ "${FLEET_DOC_FAST:-1}" = "1" ] || return 1
  [ -n "$remote_sha" ] && [ "$remote_sha" != "$ZERO" ] || return 1
  git cat-file -e "$remote_sha" 2>/dev/null || return 1
  git merge-base --is-ancestor "$remote_sha" "$local_sha" 2>/dev/null || return 1
  files="$(git diff --name-only "$remote_sha" "$local_sha")" || return 1
  [ -n "$files" ] || return 1
  while IFS= read -r f; do
    case "$f" in
      docs/*) ;;
      .github/*.md) ;;
      *.md | *.mdx | *.markdown) [ "${f%/*}" = "$f" ] || return 1 ;;
      LICENSE | LICENSE.*) ;;
      *) return 1 ;;
    esac
  done <<<"$files"
  return 0
}
if prepush_doc_only "$REMOTE_SHA" "$LOCAL_SHA"; then
  echo "▶ pre-push (awesome-django-blog) → $push_to_main: docs-only change — skipping the full gate."
  exit 0
fi

echo "▶ pre-push gate (awesome-django-blog) → $push_to_main"

# The gate must run against the pinned project deps, never system Python.
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
else
  echo "✗ .venv missing — run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

# Test-only Django settings (mirror the old workflow env).
export DEBUG=False
export LOGGING=False
export DJANGO_SETTINGS_MODULE=app.settings
export USE_SQLITE=True
export USE_CLOUD=False
export SECURE_SSL_REDIRECT=False
export SECRET_KEY="Not applicable for tests"
export ALLOWED_HOSTS="127.0.0.1 localhost"
export SITE_ID=1

echo "• ruff lint"
ruff check --config ./config/pyproject.toml app
echo "• collectstatic"
python3 manage.py collectstatic --noinput
echo "• migrate"
python3 manage.py migrate --noinput
echo "• pytest + coverage"
coverage run --rcfile=config/.coveragerc -m pytest tests
coverage report -m --skip-covered --rcfile=config/.coveragerc
echo "✓ pre-push gate complete"
