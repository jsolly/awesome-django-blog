#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { argv, exit, stderr, stdin } from "node:process";

const usage = `Usage: seo-triage.mjs --input <json-file> [--input <json-file> ...]

Normalize SEO evidence into tiered findings.

Options:
  --input   JSON evidence file. May be repeated. Use "-" for stdin.
  --help    Show this help.
`;

const tierRank = { P0: 0, P1: 1, P2: 2, P3: 3 };

function parseArgs(args) {
  const parsed = { inputs: [] };
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--input") {
      parsed.inputs.push(args[++index]);
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return parsed;
}

function fail(message) {
  stderr.write(`${message}\n`);
  exit(1);
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

async function readJson(path) {
  const text = path === "-" ? await readStdin() : await readFile(path, "utf8");
  return JSON.parse(text);
}

function textOf(value) {
  if (value == null) {
    return "";
  }
  if (typeof value === "string") {
    return value;
  }
  return JSON.stringify(value);
}

function classifyIssue(issue) {
  const haystack = [
    issue.issue,
    issue.name,
    issue.title,
    issue.category,
    issue.issue_category,
    issue.importance,
    issue.coverageState,
    issue.evidence,
    issue.url,
  ]
    .map(textOf)
    .join(" ")
    .toLowerCase();

  if (haystack.includes("redirect loop") || haystack.includes("blocked by robots") || haystack.includes("accidental noindex")) {
    return "P0";
  }
  if (haystack.includes("external")) {
    return "P3";
  }
  if (
    haystack.includes("canonical") ||
    haystack.includes("sitemap") ||
    haystack.includes("noindex") ||
    haystack.includes("4xx") ||
    haystack.includes("5xx") ||
    haystack.includes("broken")
  ) {
    return "P1";
  }
  if (haystack.includes("http to https") || haystack.includes("3xx redirect")) {
    return "P3";
  }
  if (haystack.includes("meta description") || haystack.includes("alt") || haystack.includes("social")) {
    return "P2";
  }
  return "P2";
}

function sourceOf(payload, item) {
  if (item.source) {
    return item.source;
  }
  if (payload.results?.[0]?.inspectionResult || item.inspectionResult) {
    return "gsc";
  }
  if (payload.issues || item.issue_id || item.importance) {
    return "ahrefs";
  }
  if (payload.squirrel || item.ruleId || item.rule_id) {
    return "squirrel";
  }
  return "unknown";
}

function extractItems(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }
  if (Array.isArray(payload.issues)) {
    return payload.issues;
  }
  if (Array.isArray(payload.results)) {
    return payload.results;
  }
  if (Array.isArray(payload.findings)) {
    return payload.findings;
  }
  if (Array.isArray(payload.items)) {
    return payload.items;
  }
  return [payload];
}

function normalizeUrl(item) {
  return item.url ?? item.page ?? item.inspectionUrl ?? item.target ?? item.finalUrl ?? null;
}

function normalizeFinding(payload, item) {
  const source = sourceOf(payload, item);
  const result = item.result?.inspectionResult?.indexStatusResult ?? item.inspectionResult?.indexStatusResult;
  const merged = result ? { ...item, coverageState: result.coverageState, robotsTxtState: result.robotsTxtState } : item;
  const tier = merged.tier ?? classifyIssue(merged);
  return {
    tier,
    source,
    url: normalizeUrl(merged),
    issue: merged.issue ?? merged.name ?? merged.title ?? merged.ruleId ?? merged.coverageState ?? "SEO finding",
    evidence: merged.evidence ?? merged.importance ?? merged.category ?? merged.status ?? merged.robotsTxtState ?? null,
    action: tier === "P3" ? "document" : tier === "P2" ? "schedule or batch" : "fix and verify",
  };
}

async function main() {
  let args;
  try {
    args = parseArgs(argv.slice(2));
  } catch (error) {
    fail(error.message);
  }

  if (args.help) {
    process.stdout.write(usage);
    return;
  }
  if (args.inputs.length === 0) {
    fail("Missing required --input");
  }

  const findings = [];
  for (const input of args.inputs) {
    const payload = await readJson(input);
    for (const item of extractItems(payload)) {
      findings.push(normalizeFinding(payload, item));
    }
  }

  findings.sort((a, b) => tierRank[a.tier] - tierRank[b.tier] || a.source.localeCompare(b.source));

  process.stdout.write(
    `${JSON.stringify(
      {
        count: findings.length,
        countsByTier: findings.reduce((counts, finding) => {
          counts[finding.tier] = (counts[finding.tier] ?? 0) + 1;
          return counts;
        }, {}),
        findings,
      },
      null,
      2,
    )}\n`,
  );
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
