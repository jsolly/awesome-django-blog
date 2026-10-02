// Based on dotagents/templates/github/production-smoke.mjs; this repo requires
// an exact static build marker before public behavior can establish a release.
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const REQUEST_ID = /^[a-zA-Z0-9_-]{1,100}$/u;

export function verifyResponse({ url, status }, canonical) {
	const final = new URL(url);
	const target = new URL(canonical);
	if (final.protocol !== "https:" || final.origin !== target.origin) {
		throw new Error(`Noncanonical response: ${url}`);
	}
	if (status < 200 || status >= 300) {
		throw new Error(`HTTP ${status}: ${url}`);
	}
}
export async function runSmoke({
	scenario,
	env = process.env,
	fetcher = fetch,
	launch,
	readinessMs = 120000,
	pollMs = 10000,
	behaviorMs = 90000,
}) {
	const artifacts = resolve("production-smoke-artifacts");
	await mkdir(artifacts, { recursive: true });
	const receipt = {
		requestId: env.PRODUCTION_SMOKE_REQUEST_ID,
		releaseSha: env.PRODUCTION_SMOKE_RELEASE_SHA,
		observations: [],
		errors: [],
		success: false,
	};
	let browser, context, page, timer;
	const recordError = (error) => receipt.errors.push(String(error));
	const diagnostics = [];
	const drainDiagnostics = async () => {
		for (let checked = 0; checked < diagnostics.length; ) {
			const pending = diagnostics.slice(checked);
			checked = diagnostics.length;
			await Promise.all(pending);
		}
	};
	const verifyHttp = async (url) => {
		const response = await fetcher(url, {
			redirect: "follow",
			cache: "no-store",
			signal: AbortSignal.timeout(15000),
		});
		const observation = { url: response.url, status: response.status };
		receipt.observations.push(observation);
		verifyResponse(observation, url);
		return response;
	};
	try {
		if (!REQUEST_ID.test(receipt.requestId ?? "")) {
			throw new Error("Invalid smoke request ID");
		}
		if (!/^[0-9a-f]{40}$/u.test(receipt.releaseSha ?? "")) {
			throw new Error("Invalid smoke release SHA");
		}
		if (new URL(scenario.productionUrl).protocol !== "https:") {
			throw new Error("Production URL must use HTTPS");
		}
		const deadline = Date.now() + readinessMs;
		for (;;) {
			try {
				await verifyHttp(scenario.productionUrl);
				await scenario.verifyRelease({ verifyHttp, releaseSha: receipt.releaseSha });
				break;
			} catch (error) {
				if (Date.now() >= deadline) {
					throw new Error(`Readiness deadline: ${error}`, {
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
		// Routing disables the HTTP cache so every document comes from the network.
		await context.route("**/*", (route) => route.continue());
		await context.tracing.start({
			screenshots: true,
			snapshots: true,
			sources: true,
		});
		page = await context.newPage();
		page.setDefaultTimeout(15000);
		const origin = new URL(scenario.productionUrl).origin;
		page.on("console", (message) => {
			if (message.type() === "error") {
				recordError(`console: ${message.text()}`);
			}
		});
		page.on("pageerror", (error) => recordError(`pageerror: ${error}`));
		page.on("requestfailed", (request) => {
			if (new URL(request.url()).origin !== origin) {
				return;
			}
			diagnostics.push(
				(async () => {
					const failure = request.failure()?.errorText;
					if (request.method() === "HEAD" && failure === "net::ERR_ABORTED") {
						// Chromium can abort a HEAD body after receiving its successful headers.
						const response = await request.response();
						if (
							response &&
							response.status() >= 200 &&
							response.status() < 300
						) {
							receipt.observations.push({
								url: response.url(),
								status: response.status(),
								source: "browser-head",
								method: "HEAD",
							});
							return;
						}
					}
					recordError(`requestfailed: ${request.url()} ${failure}`);
				})().catch(recordError),
			);
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
				receipt.observations.push({
					url: response.url(),
					status: response.status(),
					source: "browser",
				});
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
					{ url: response.url(), status: response.status() },
					scenario.productionUrl,
				);
				await scenario.smoke({ page, context, artifacts, verifyHttp });
				await drainDiagnostics();
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
		await drainDiagnostics();
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
