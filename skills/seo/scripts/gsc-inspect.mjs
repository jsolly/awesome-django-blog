#!/usr/bin/env node
import { createSign } from "node:crypto";
import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import { argv, env, exit, stderr, stdin } from "node:process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

const usage = `Usage: gsc-inspect.mjs --site-url <property-url> (--url <url> | --url-file <file> | --stdin)

Batch Google Search Console URL Inspection requests as JSON.

Environment:
  GSC_ACCESS_TOKEN                Preferred bearer token.
  GSC_QUOTA_PROJECT               GCP project ID for ADC quota/billing headers.
  GOOGLE_APPLICATION_CREDENTIALS Optional service account JSON path.

Options:
  --site-url    GSC property URL, e.g. https://www.example.com/
  --url         URL to inspect. May be repeated.
  --url-file    File containing one URL per line.
  --stdin       Read one URL per line from stdin.
  --max         Maximum URLs to inspect. Default: 200.
  --delay-ms    Delay between calls. Default: 100.
  --check-auth
               Verify GSC credentials resolve without printing a token.
  --help        Show this help.
`;

function parseArgs(args) {
  const parsed = { urls: [], max: 200, delayMs: 100 };
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--site-url") {
      parsed.siteUrl = args[++index];
    } else if (arg === "--url") {
      parsed.urls.push(args[++index]);
    } else if (arg === "--url-file") {
      parsed.urlFile = args[++index];
    } else if (arg === "--stdin") {
      parsed.stdin = true;
    } else if (arg === "--max") {
      parsed.max = Number.parseInt(args[++index] ?? "", 10);
    } else if (arg === "--delay-ms") {
      parsed.delayMs = Number.parseInt(args[++index] ?? "", 10);
    } else if (arg === "--check-auth") {
      parsed.checkAuth = true;
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

function base64url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replaceAll("+", "-")
    .replaceAll("/", "_")
    .replaceAll("=", "");
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString("utf8");
}

async function getAccessToken() {
  if (env.GSC_ACCESS_TOKEN) {
    return env.GSC_ACCESS_TOKEN;
  }

  if (env.GOOGLE_APPLICATION_CREDENTIALS) {
    const credentials = JSON.parse(await readFile(env.GOOGLE_APPLICATION_CREDENTIALS, "utf8"));
    if (!credentials.client_email || !credentials.private_key) {
      fail("GOOGLE_APPLICATION_CREDENTIALS must contain client_email and private_key");
    }

    const now = Math.floor(Date.now() / 1000);
    const header = { alg: "RS256", typ: "JWT" };
    const payload = {
      iss: credentials.client_email,
      scope: "https://www.googleapis.com/auth/webmasters",
      aud: "https://oauth2.googleapis.com/token",
      iat: now,
      exp: now + 3600,
    };
    const unsigned = `${base64url(JSON.stringify(header))}.${base64url(JSON.stringify(payload))}`;
    const signer = createSign("RSA-SHA256");
    signer.update(unsigned);
    signer.end();
    const assertion = `${unsigned}.${base64url(signer.sign(credentials.private_key))}`;

    const response = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion,
      }),
    });
    const token = await response.json();
    if (!response.ok) {
      const message = token.error_description ?? token.error ?? `HTTP ${response.status}`;
      fail(`Google token endpoint returned ${response.status}: ${message}`);
    }
    return token.access_token;
  }

  try {
    const { stdout } = await execFileAsync("gcloud", [
      "auth",
      "application-default",
      "print-access-token",
    ]);
    const token = stdout.trim();
    if (token) {
      return token;
    }
  } catch (error) {
    const detail = error.stderr?.trim() || error.message;
    fail(`Missing GSC_ACCESS_TOKEN, GOOGLE_APPLICATION_CREDENTIALS, or gcloud ADC auth. gcloud detail: ${detail}`);
  }

  fail("Missing GSC_ACCESS_TOKEN, GOOGLE_APPLICATION_CREDENTIALS, or gcloud ADC auth");
}

async function resolveQuotaProject() {
  if (env.GSC_QUOTA_PROJECT) {
    return env.GSC_QUOTA_PROJECT;
  }

  const adcPath = `${env.HOME}/.config/gcloud/application_default_credentials.json`;
  try {
    const adc = JSON.parse(await readFile(adcPath, "utf8"));
    if (adc.quota_project_id) {
      return adc.quota_project_id;
    }
  } catch {
    // ADC file absent or unreadable; fall through.
  }

  try {
    const { stdout } = await execFileAsync("gcloud", [
      "auth",
      "application-default",
      "print-quota-project",
    ]);
    const project = stdout.trim();
    if (project) {
      return project;
    }
  } catch {
    // gcloud unavailable or quota project unset.
  }

  return undefined;
}

function normalizeLines(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));
}

function isHttpUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

async function collectUrls(args) {
  const urls = [...args.urls];
  if (args.urlFile) {
    urls.push(...normalizeLines(await readFile(args.urlFile, "utf8")));
  }
  if (args.stdin) {
    urls.push(...normalizeLines(await readStdin()));
  }
  const validUrls = [];
  for (const url of urls) {
    if (isHttpUrl(url)) {
      validUrls.push(url);
      continue;
    }
    stderr.write(`Skipping non-URL line: ${url}\n`);
  }
  return [...new Set(validUrls)].slice(0, args.max);
}

async function sleep(ms) {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function inspectUrl({ token, quotaProject, siteUrl, url }) {
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  if (quotaProject) {
    headers["x-goog-user-project"] = quotaProject;
  }

  const response = await fetch("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", {
    method: "POST",
    headers,
    body: JSON.stringify({
      inspectionUrl: url,
      siteUrl,
      languageCode: "en-US",
    }),
  });
  const body = await response.json();
  return {
    url,
    ok: response.ok,
    status: response.status,
    result: body,
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

  if (args.checkAuth) {
    await getAccessToken();
    process.stdout.write("GSC auth ready\n");
    return;
  }

  if (!args.siteUrl) {
    fail("Missing required --site-url");
  }
  if (!Number.isInteger(args.max) || args.max < 1 || args.max > 200) {
    fail("--max must be an integer from 1 to 200");
  }
  if (!Number.isInteger(args.delayMs) || args.delayMs < 0) {
    fail("--delay-ms must be a non-negative integer");
  }

  const urls = await collectUrls(args);
  if (urls.length === 0) {
    fail("Provide at least one --url, --url-file, or --stdin URL");
  }

  const token = await getAccessToken();
  const quotaProject = await resolveQuotaProject();
  const results = [];
  for (const url of urls) {
    stderr.write(`Inspecting ${url}\n`);
    results.push(await inspectUrl({ token, quotaProject, siteUrl: args.siteUrl, url }));
    if (args.delayMs > 0) {
      await sleep(args.delayMs);
    }
  }

  process.stdout.write(`${JSON.stringify({ siteUrl: args.siteUrl, count: results.length, results }, null, 2)}\n`);
}

main().catch((error) => {
  fail(error instanceof Error ? error.message : String(error));
});
