#!/usr/bin/env bash
# Assert a Biome config carries the backend Lambda lint contract.
#
# Without this guard, a Biome version bump that renames or graduates a nursery
# rule (noFloatingPromises lives in nursery today) silently drops enforcement.
# Shipped in .agents/scripts/ via the dotagents fleet subtree.
#
# Usage:
#   check-biome-rules.sh                     # checks ./biome.jsonc
#   check-biome-rules.sh path/to/biome.jsonc # explicit path

set -euo pipefail

BIOME_FILE="${1:-biome.jsonc}"
if [[ ! -f "$BIOME_FILE" ]]; then
	printf '\033[0;31mbiome config not found: %s\033[0m\n' "$BIOME_FILE" >&2
	exit 1
fi

node --input-type=module -e "
	import { readFileSync } from 'node:fs';
	const path = process.argv[1];
	// Strip JSONC comments (line + block) before parsing. Conservative regex —
	// won't handle a // sequence inside a string, but biome configs don't use
	// strings containing //.
	const raw = readFileSync(path, 'utf8')
		.replace(/\/\\*[\s\S]*?\\*\//g, '')
		.replace(/^[\\s]*\/\/.*$/gm, '');
	const config = JSON.parse(raw);
	const rules = config?.linter?.rules ?? {};
	const groups = ['suspicious', 'style', 'nursery', 'correctness', 'a11y', 'complexity', 'performance', 'security'];
	const required = ['noConsole', 'noEmptyBlockStatements', 'useThrowOnlyError', 'noFloatingPromises'];
	const missing = [];
	for (const rule of required) {
		let found = false;
		for (const group of groups) {
			const val = rules[group]?.[rule];
			if (val === 'error' || (val && typeof val === 'object' && val.level === 'error')) {
				found = true;
				break;
			}
		}
		if (!found) missing.push(rule);
	}
	if (missing.length > 0) {
		const red = '\\u001b[0;31m';
		const reset = '\\u001b[0m';
		for (const m of missing) {
			process.stderr.write(\`  \${red}✗\${reset} \${path} missing required rule at error level: \${m}\n\`);
		}
		process.stderr.write(\`\${red}\${path} missing backend Lambda lint contract (noConsole, noEmptyBlockStatements, useThrowOnlyError, noFloatingPromises at error).\${reset}\n\`);
		process.exit(1);
	}
" "$BIOME_FILE"
