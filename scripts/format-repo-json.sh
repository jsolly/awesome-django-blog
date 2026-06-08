#!/usr/bin/env bash
# Apply the repo's Biome formatter to JSON files after jq rewrites them.
# jq defaults to 2-space indent; tab-indent Biome configs would otherwise stage
# whitespace-only diffs that lint-staged reverts at commit time.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

[[ $# -gt 0 ]] || exit 0

if [[ ! -f biome.json && ! -f biome.jsonc ]]; then
	exit 0
fi

biome_cmd=()
if [[ -x node_modules/.bin/biome ]]; then
	biome_cmd=(node_modules/.bin/biome)
elif [[ -f package.json ]] && command -v pnpm >/dev/null 2>&1; then
	if pnpm exec biome --version >/dev/null 2>&1; then
		biome_cmd=(pnpm exec biome)
	fi
fi
if [[ ${#biome_cmd[@]} -eq 0 ]] && command -v biome >/dev/null 2>&1; then
	if biome --version >/dev/null 2>&1; then
		biome_cmd=(biome)
	fi
fi
if [[ ${#biome_cmd[@]} -eq 0 ]] && command -v npx >/dev/null 2>&1; then
	if npx --no @biomejs/biome -- --version >/dev/null 2>&1; then
		biome_cmd=(npx --no @biomejs/biome)
	fi
fi

if [[ ${#biome_cmd[@]} -eq 0 ]]; then
	echo "format-repo-json: biome.json(c) present but Biome not found; leaving jq formatting" >&2
	exit 0
fi

existing=()
for f in "$@"; do
	[[ -f "$f" ]] && existing+=("$f")
done
[[ ${#existing[@]} -gt 0 ]] || exit 0

"${biome_cmd[@]}" format --write "${existing[@]}"
