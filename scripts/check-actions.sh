#!/usr/bin/env bash
# Lint GitHub Actions workflows with actionlint + shellcheck.
#
# actionlint comes from the npm lockfile. ShellCheck's official release archive
# is pinned by version and SHA-256 below; verify it before extraction/execution.
# The verified archive is cached inside node_modules for local/CI parity.
#
# Copy into each workflow repo as scripts/check-actions.sh, then:
#   "check:actions": "bash scripts/check-actions.sh"
# in package.json, plus `run_step "actionlint" npm run check:actions` in
# .git-hooks/pre-commit and `- run: npm run check:actions` in ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ACTIONLINT="$ROOT/node_modules/.bin/github-actionlint"
SHELLCHECK_VERSION=v0.11.0

if [[ ! -x "$ACTIONLINT" ]]; then
	echo "✗ github-actionlint not found at $ACTIONLINT — run npm ci" >&2
	exit 1
fi
case "$(uname -s):$(uname -m)" in
  Darwin:arm64) platform=darwin.aarch64; digest=339b930feb1ea764467013cc1f72d09cd6b869ebf1013296ba9055ab2ffbd26f ;;
  Darwin:x86_64) platform=darwin.x86_64; digest=c2c15e08df0e8fbc374c335b230a7ee958c313fa5714817a59aa59f1aa594f51 ;;
  Linux:aarch64|Linux:arm64) platform=linux.aarch64; digest=68a8133197a50beb8803f8d42f9908d1af1c5540d4bb05fdfca8c1fa47decefc ;;
  Linux:x86_64) platform=linux.x86_64; digest=b7af85e41cc99489dcc21d66c6d5f3685138f06d34651e6d34b42ec6d54fe6f6 ;;
  *) echo "Unsupported ShellCheck platform: $(uname -s) $(uname -m)" >&2; exit 1 ;;
esac
cache="$ROOT/node_modules/.cache/shellcheck/$SHELLCHECK_VERSION/$platform"
mkdir -p "$cache"
archive="$cache/release.tar.gz"
work="$(mktemp -d "$cache/run.XXXXXX")"
trap 'rm -rf "$work"' EXIT
if [[ ! -f "$archive" ]]; then
  curl --fail --location --silent --show-error \
    "https://github.com/koalaman/shellcheck/releases/download/$SHELLCHECK_VERSION/shellcheck-$SHELLCHECK_VERSION.$platform.tar.gz" \
    --output "$work/download.tar.gz"
  archive="$work/download.tar.gz"
fi
actual="$(shasum -a 256 "$archive")"
if [[ "${actual%% *}" != "$digest" ]]; then
  echo "ShellCheck archive checksum mismatch: $archive (remove it and retry)" >&2
  exit 1
fi
if [[ "$archive" == "$work/download.tar.gz" ]]; then
  mv "$archive" "$cache/release.tar.gz"
  archive="$cache/release.tar.gz"
fi
tar -xzf "$archive" -C "$work"
SHELLCHECK="$work/shellcheck-$SHELLCHECK_VERSION/shellcheck"

# github-actionlint 1.7.x bundles pre-v3.1 create-github-app-token metadata (no
# client-id; app-id still required). Workflows retain app-id alongside client-id.
# Drop this -ignore flag when actionlint's popular-actions registry catches up
# (rhysd/actionlint#652 / #668).
"$ACTIONLINT" -shellcheck "$SHELLCHECK" \
	-ignore 'input "client-id" is not defined in action "actions/create-github-app-token@' \
	.github/workflows/*.yml
