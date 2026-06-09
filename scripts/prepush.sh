#!/usr/bin/env bash
# Pre-push gate for awesome-django-blog (Python/Django).
#
# Invoked by .git-hooks/pre-push (core.hooksPath=.git-hooks). Replaces the
# `build` job of the old .github/workflows/django-test-deploy-master.yaml: the
# lint + test gate now runs locally on push to master. CodeQL was dropped;
# deploy is handled by the hosting provider on push to master, unchanged.
#
# Only acts on a non-deleting push to main/master; feature-branch pushes stay
# fast. Escape hatch: FLEET_SKIP_PREPUSH=1 git push (audited).
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
while read -r _local_ref local_sha remote_ref _remote_sha; do
  case "$remote_ref" in
    refs/heads/main | refs/heads/master)
      [ "$local_sha" = "$ZERO" ] && continue
      push_to_main="$remote_ref"
      ;;
  esac
done
[ -z "$push_to_main" ] && exit 0

echo "▶ pre-push gate (awesome-django-blog) → $push_to_main"

# Activate the project virtualenv if present (CI created one per-run).
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
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
ruff --config ./config/pyproject.toml app
echo "• collectstatic"
python3 manage.py collectstatic --noinput
echo "• migrate"
python3 manage.py migrate --noinput
echo "• pytest + coverage"
coverage run --rcfile=config/.coveragerc -m pytest tests
echo "✓ pre-push gate complete"
