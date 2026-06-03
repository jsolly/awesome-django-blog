#!/usr/bin/env bash
# Mirrors django-test-deploy-master.yaml build job after ruff (collectstatic, migrate, pytest).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export DEBUG=False LOGGING=False DJANGO_SETTINGS_MODULE=app.settings USE_SQLITE=True USE_CLOUD=False SECURE_SSL_REDIRECT=False
export SECRET_KEY="local-pre-commit" ALLOWED_HOSTS="127.0.0.1 localhost" SITE_ID=1

if [[ ! -d .venv ]]; then
  echo "Error: .venv missing. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate

python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
coverage run --rcfile=config/.coveragerc -m pytest tests
