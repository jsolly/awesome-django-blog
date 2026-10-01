#!/usr/bin/env bash
# Lint GitHub Actions workflows with actionlint + ShellCheck.
#
# Both tools come from official release archives pinned by version and SHA-256
# per platform below, never from an npm wrapper: neither upstream release is
# immutable. Each archive is verified before extraction/execution, and verified
# archives are cached by digest inside node_modules for local/CI parity. Nothing
# outside the pins changes the lint: actionlint's pyflakes rule stays off, and a
# caller's SHELLCHECK_OPTS is dropped.
#
# Copy byte-identical into each workflow repo as scripts/check-actions.sh, then:
#   "check:actions": "bash scripts/check-actions.sh"
# in package.json, plus `run_step "actionlint" npm run check:actions` in
# .git-hooks/pre-commit. Every templates/github/ci-*.yml already runs
# `npm run check:actions` after actions/checkout. No npm dependency.
set -euo pipefail
unset SHELLCHECK_OPTS

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# actionlint lints the nearest ancestor holding both, so anywhere else it would lint a parent repo.
if [[ ! -d .github/workflows || ! -e .git ]]; then
  echo "✗ $ROOT is not a repository root with .github/workflows — run this as <repo>/scripts/check-actions.sh" >&2
  exit 1
fi

ACTIONLINT_VERSION=v1.7.12
SHELLCHECK_VERSION=v0.11.0

case "$(uname -s):$(uname -m)" in
  Darwin:arm64)
    actionlint_platform=darwin_arm64 actionlint_digest=aba9ced2dee8d27fecca3dc7feb1a7f9a52caefa1eb46f3271ea66b6e0e6953f
    shellcheck_platform=darwin.aarch64 shellcheck_digest=339b930feb1ea764467013cc1f72d09cd6b869ebf1013296ba9055ab2ffbd26f ;;
  Darwin:x86_64)
    actionlint_platform=darwin_amd64 actionlint_digest=5b44c3bc2255115c9b69e30efc0fecdf498fdb63c5d58e17084fd5f16324c644
    shellcheck_platform=darwin.x86_64 shellcheck_digest=c2c15e08df0e8fbc374c335b230a7ee958c313fa5714817a59aa59f1aa594f51 ;;
  Linux:aarch64|Linux:arm64)
    actionlint_platform=linux_arm64 actionlint_digest=325e971b6ba9bfa504672e29be93c24981eeb1c07576d730e9f7c8805afff0c6
    shellcheck_platform=linux.aarch64 shellcheck_digest=68a8133197a50beb8803f8d42f9908d1af1c5540d4bb05fdfca8c1fa47decefc ;;
  Linux:x86_64)
    actionlint_platform=linux_amd64 actionlint_digest=8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8
    shellcheck_platform=linux.x86_64 shellcheck_digest=b7af85e41cc99489dcc21d66c6d5f3685138f06d34651e6d34b42ec6d54fe6f6 ;;
  *) echo "✗ Unsupported actionlint/ShellCheck platform: $(uname -s) $(uname -m)" >&2; exit 1 ;;
esac

cache="$ROOT/node_modules/.cache/check-actions"
mkdir -p "$cache"
work="$(mktemp -d "$cache/run.XXXXXX")"
trap 'rm -rf "$work"' EXIT

# unpack <tool> <sha256> <url>: extract the verified release archive into $work/<tool>.
# The cache is keyed by digest, and only a download that matches the digest enters it.
unpack() {
  local tool="$1" digest="$2" url="$3" cached="$cache/$1-$2.tar.gz"
  if [[ -f "$cached" ]]; then
    shasum -a 256 -c --status <<<"$digest  $cached" \
      || { echo "✗ cached $tool archive is corrupt: remove $cached and rerun" >&2; exit 1; }
  else
    curl --fail --location --silent --show-error --connect-timeout 10 --max-time 120 "$url" --output "$work/$tool.tar.gz" \
      || { echo "✗ could not download $tool from $url (the first run after npm ci needs network)" >&2; exit 1; }
    shasum -a 256 -c --status <<<"$digest  $work/$tool.tar.gz" \
      || { echo "✗ $tool from $url does not match its pinned SHA-256 — verify the upstream release before changing the pin" >&2; exit 1; }
    mv "$work/$tool.tar.gz" "$cached"
  fi
  mkdir "$work/$tool"
  tar -xzf "$cached" -C "$work/$tool"
}

unpack shellcheck "$shellcheck_digest" \
  "https://github.com/koalaman/shellcheck/releases/download/$SHELLCHECK_VERSION/shellcheck-$SHELLCHECK_VERSION.$shellcheck_platform.tar.gz"
SHELLCHECK="$work/shellcheck/shellcheck-$SHELLCHECK_VERSION/shellcheck"
# actionlint silently disables its shellcheck rule when -shellcheck cannot run (exit 0, noted
# only under -verbose), so prove the verified binary runs before handing it over.
if [[ ! -x "$SHELLCHECK" ]] || ! "$SHELLCHECK" --version >/dev/null; then
  echo "✗ verified ShellCheck $SHELLCHECK_VERSION ($shellcheck_platform) does not run here (noexec node_modules mount or a missing library?) — actionlint would skip every SC* rule" >&2
  exit 1
fi

unpack actionlint "$actionlint_digest" \
  "https://github.com/rhysd/actionlint/releases/download/$ACTIONLINT_VERSION/actionlint_${ACTIONLINT_VERSION#v}_$actionlint_platform.tar.gz"
# No file arguments: actionlint lints every .yml and .yaml workflow under .github/workflows.
"$work/actionlint/actionlint" -shellcheck "$SHELLCHECK" -pyflakes=
