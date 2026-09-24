// Canonical source: dotagents/templates/github/production-smoke.mjs
import { execFileSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

// Retain read-only checkout authentication only for git; never inherit it in Chromium.
const FULL_SHA = /^[a-f0-9]{40}$/iu;
const RELEASE_SHA = /^[a-f0-9]{7,40}$/iu;
const REQUEST_ID = /^[a-zA-Z0-9_-]{1,100}$/u;
const fetchToken = process.env.PRODUCTION_SMOKE_GITHUB_TOKEN;
delete process.env.PRODUCTION_SMOKE_GITHUB_TOKEN;

export function fullSha(value) {
	if (!FULL_SHA.test(value ?? "")) {
		throw new Error("Expected full 40-character commit SHA");
	}
	return value.toLowerCase();
}
export function verifyAncestry(expected, observed, git = execFileSync) {
	fullSha(expected);
	if (!RELEASE_SHA.test(observed ?? "")) {
		throw new Error(`Invalid release identity: ${observed}`);
	}
	let actual;
	try {
		actual = git("git", ["rev-parse", "--verify", `${observed}^{commit}`], {
			encoding: "utf8",
		}).trim();
	} catch {
		// A newer production deploy may land after this workflow checked out main.
		git("git", ["fetch", "--no-tags", "origin", "main"], {
			timeout: 15000,
			env: fetchToken
				? {
						...process.env,
						GIT_CONFIG_COUNT: "1",
						GIT_CONFIG_KEY_0: "http.https://github.com/.extraheader",
						GIT_CONFIG_VALUE_0: `AUTHORIZATION: basic ${Buffer.from(`x-access-token:${fetchToken}`).toString("base64")}`,
					}
				: process.env,
		});
		actual = git("git", ["rev-parse", "--verify", `${observed}^{commit}`], {
			encoding: "utf8",
		}).trim();
	}
	fullSha(actual);
	git("git", ["merge-base", "--is-ancestor", expected, actual]);
	return actual;
}
export function verifyResponse(
	{ url, status, release },
	canonical,
	expected,
	git,
) {
	const final = new URL(url);
	const target = new URL(canonical);
	if (final.protocol !== "https:" || final.origin !== target.origin) {
		throw new Error(`Noncanonical response: ${url}`);
	}
	if (status < 200 || status >= 300) {
		throw new Error(`HTTP ${status}: ${url}`);
	}
	return verifyAncestry(expected, release, git);
}
export async function runSmoke({
	scenario,
	env = process.env,
	fetcher = fetch,
	launch,
	git = execFileSync,
	readinessMs = 600000,
	pollMs = 10000,
	behaviorMs = 90000,
}) {
	const artifacts = resolve("production-smoke-artifacts");
	await mkdir(artifacts, { recursive: true });
	const receipt = {
		expectedSha: env.PRODUCTION_SMOKE_SHA,
		expectedServerSha: env.PRODUCTION_SMOKE_SERVER_SHA || null,
		requestId: env.PRODUCTION_SMOKE_REQUEST_ID,
		observations: [],
		errors: [],
		success: false,
	};
	let browser, context, page, timer;
	const recordError = (error) => receipt.errors.push(String(error));
	const verifyRelease = async (url, minimumSha = receipt.expectedSha) => {
		const response = await fetcher(url, {
			redirect: "follow",
			cache: "no-store",
			signal: AbortSignal.timeout(15000),
		});
		const observation = {
			url: response.url,
			status: response.status,
			release: response.headers.get("x-release-id"),
			minimumSha,
		};
		receipt.observations.push(observation);
		observation.commit = verifyResponse(observation, url, minimumSha, git);
		return response;
	};
	try {
		fullSha(receipt.expectedSha);
		if (receipt.expectedServerSha) {
			fullSha(receipt.expectedServerSha);
		}
		if (!REQUEST_ID.test(receipt.requestId ?? "")) {
			throw new Error("Invalid smoke request ID");
		}
		git("git", [
			"merge-base",
			"--is-ancestor",
			receipt.expectedSha,
			"origin/main",
		]);
		if (new URL(scenario.productionUrl).protocol !== "https:") {
			throw new Error("Production URL must use HTTPS");
		}
		const deadline = Date.now() + readinessMs;
		for (;;) {
			try {
				await verifyRelease(scenario.productionUrl);
				break;
			} catch (error) {
				if (Date.now() >= deadline) {
					throw new Error(`Release readiness deadline: ${error}`, {
						cause: error,
					});
				}
				await new Promise((resolveWait) =>
					setTimeout(resolveWait, Math.min(pollMs, deadline - Date.now())),
				);
			}
		}
		browser = await (
			launch ?? (async () => (await import("playwright")).chromium.launch())
		)();
		context = await browser.newContext({ serviceWorkers: "block" });
		// Routing disables HTTP cache so each document supplies its network release header.
		await context.route("**/*", (route) => route.continue());
		await context.tracing.start({
			screenshots: true,
			snapshots: true,
			sources: true,
		});
		page = await context.newPage();
		page.setDefaultTimeout(15000);
		const origin = new URL(scenario.productionUrl).origin;
		const documents = [];
		page.on("console", (message) => {
			if (message.type() === "error") {
				recordError(`console: ${message.text()}`);
			}
		});
		page.on("pageerror", (error) => recordError(`pageerror: ${error}`));
		page.on("requestfailed", (request) => {
			if (new URL(request.url()).origin === origin) {
				recordError(
					`requestfailed: ${request.url()} ${request.failure()?.errorText}`,
				);
			}
		});
		page.on("response", (response) => {
			if (new URL(response.url()).origin !== origin) {
				return;
			}
			if (response.status() >= 400) {
				recordError(`HTTP ${response.status()}: ${response.url()}`);
			}
			if (
				response.request().resourceType() === "document" &&
				response.status() >= 200 &&
				response.status() < 300
			) {
				documents.push(
					(async () => {
						const observation = {
							url: response.url(),
							status: response.status(),
							release: await response.headerValue("x-release-id"),
							source: "browser",
						};
						receipt.observations.push(observation);
						verifyResponse(
							observation,
							scenario.productionUrl,
							receipt.expectedSha,
							git,
						);
					})().catch(recordError),
				);
			}
		});
		await Promise.race([
			(async () => {
				const response = await page.goto(scenario.productionUrl, {
					waitUntil: "domcontentloaded",
				});
				if (!response) {
					throw new Error("Navigation returned no document");
				}
				verifyResponse(
					{
						url: response.url(),
						status: response.status(),
						release: await response.headerValue("x-release-id"),
					},
					scenario.productionUrl,
					receipt.expectedSha,
					git,
				);
				await scenario.smoke({
					page,
					context,
					artifacts,
					expectedSha: receipt.expectedSha,
					expectedServerSha: receipt.expectedServerSha,
					verifyRelease,
				});
				await Promise.all(documents);
				await verifyRelease(scenario.productionUrl);
				if (receipt.errors.length) {
					throw new Error("Browser diagnostics failed");
				}
			})(),
			new Promise((_, reject) => {
				timer = setTimeout(
					() => reject(new Error("Behavior deadline exceeded")),
					behaviorMs,
				);
			}),
		]);
		receipt.success = true;
	} catch (error) {
		recordError(error);
	} finally {
		clearTimeout(timer);
		if (page) {
			await page
				.screenshot({ path: resolve(artifacts, "page.png"), fullPage: true })
				.catch(recordError);
		}
		if (context) {
			await context.tracing
				.stop({ path: resolve(artifacts, "trace.zip") })
				.catch(recordError);
		}
		if (browser) {
			await browser.close().catch(recordError);
		}
		if (receipt.errors.length) {
			receipt.success = false;
		}
		await writeFile(
			resolve(artifacts, "receipt.json"),
			`${JSON.stringify(receipt, null, 2)}\n`,
		);
	}
	return receipt;
}
if (
	process.argv[1] &&
	import.meta.url === pathToFileURL(resolve(process.argv[1])).href
) {
	try {
		const scenario = await import(
			pathToFileURL(resolve("scripts/production-smoke-scenario.mjs")).href
		);
		const receipt = await runSmoke({ scenario });
		process.stdout.write(`${JSON.stringify(receipt, null, 2)}\n`);
		if (!receipt.success) {
			process.exitCode = 1;
		}
	} catch (error) {
		process.stderr.write(`${error}\n`);
		process.exitCode = 1;
	}
}
