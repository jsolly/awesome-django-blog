#!/usr/bin/env node
import { argv, env, exit, stderr } from "node:process";

const usage = `Usage: ahrefs-issues.mjs --project-id <id> [--date-compared <iso-or-timestamp>]

Fetch Ahrefs Site Audit issues as JSON.

Environment:
  AHREFS_API_TOKEN   Required bearer token for Ahrefs API v3.

Options:
  --project-id       Ahrefs Site Audit project ID.
  --date-compared    Optional comparison crawl date/timestamp.
  --help             Show this help.
`;

function parseArgs(args) {
  const parsed = {};
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--project-id") {
      parsed.projectId = args[++index];
    } else if (arg === "--date-compared") {
      parsed.dateCompared = args[++index];
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

  if (!args.projectId) {
    fail("Missing required --project-id");
  }

  if (!env.AHREFS_API_TOKEN) {
    fail("Missing required AHREFS_API_TOKEN");
  }

  const url = new URL("https://api.ahrefs.com/v3/site-audit/issues");
  url.searchParams.set("project_id", args.projectId);
  url.searchParams.set("output", "json");
  if (args.dateCompared) {
    url.searchParams.set("date_compared", args.dateCompared);
  }

  stderr.write(`Fetching Ahrefs issues for project ${args.projectId}\n`);
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${env.AHREFS_API_TOKEN}`,
      Accept: "application/json",
    },
  });

  const body = await response.text();
  if (!response.ok) {
    const detail = body.length > 200 ? `${body.slice(0, 200)}…` : body;
    fail(`Ahrefs API returned ${response.status}: ${detail}`);
  }

  process.stdout.write(`${body}\n`);
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
