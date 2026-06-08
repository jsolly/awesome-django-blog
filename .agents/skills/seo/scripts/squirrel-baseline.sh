#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: squirrel-baseline.sh <pre|post> <site-url> <output-dir> [coverage]

Run a Squirrel SEO baseline and write artifacts under output-dir.

Arguments:
  pre|post      Baseline label.
  site-url      Site URL to crawl.
  output-dir    Directory for artifacts.
  coverage      Optional coverage mode. Default: surface.

Environment:
  SQUIRREL_BIN  Optional squirrel binary path/name. Default: squirrel.

Outputs:
  <output-dir>/<label>-squirrel.llm
  <output-dir>/<label>-squirrel.json
USAGE
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

label="${1:-}"
site_url="${2:-}"
output_dir="${3:-}"
coverage="${4:-surface}"
squirrel_bin="${SQUIRREL_BIN:-squirrel}"

if [[ "$label" != "pre" && "$label" != "post" ]]; then
  echo "First argument must be pre or post" >&2
  usage >&2
  exit 1
fi

if [[ -z "$site_url" || -z "$output_dir" ]]; then
  echo "Missing site-url or output-dir" >&2
  usage >&2
  exit 1
fi

if ! command -v "$squirrel_bin" >/dev/null 2>&1; then
  echo "Missing squirrel CLI. Install Squirrel or set SQUIRREL_BIN." >&2
  exit 1
fi

if [[ "$output_dir" == *".."* ]]; then
  echo "output-dir must not contain .." >&2
  exit 1
fi

mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"

"$squirrel_bin" self doctor >&2

llm_out="$output_dir/$label-squirrel.llm"
json_out="$output_dir/$label-squirrel.json"

echo "Running Squirrel $label baseline for $site_url (coverage: $coverage)" >&2
"$squirrel_bin" audit "$site_url" --coverage "$coverage" --format llm --refresh -o "$llm_out" >&2
"$squirrel_bin" audit "$site_url" --coverage "$coverage" --format json --refresh -o "$json_out" >&2

node -e '
const [label, siteUrl, coverage, llm, json] = process.argv.slice(1);
console.log(JSON.stringify({ label, siteUrl, coverage, llm, json }));
' "$label" "$site_url" "$coverage" "$llm_out" "$json_out"
