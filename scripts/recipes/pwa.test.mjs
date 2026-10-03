import { before, after, test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, cp, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { pathToFileURL } from 'node:url';
import { resolve, extname, join } from 'node:path';
import { chromium } from 'playwright';
import { recipeRoute, buildRecipePwa } from './pwa-build.mjs';

let server, browser, origin, fixture;
const snapshots = [];
let version = 1;
let failDownload = false;
const root = resolve('dist');
before(async () => {
  fixture = await mkdtemp(join(tmpdir(), 'recipe-pwa-test-'));
  for (const label of ['A', 'B']) {
    const directory = join(fixture, label);
    await cp(root, directory, { recursive: true });
    const htmlPath = `${directory}${recipeRoute}index.html`;
    const html = (await readFile(htmlPath, 'utf8')).replace('</head>', `<meta name="pwa-test-snapshot" content="${label}"></head>`);
    await writeFile(htmlPath, html);
    const dataPath = `${directory}/data/recipe-library.json`;
    const data = JSON.parse(await readFile(dataPath, 'utf8'));
    await writeFile(dataPath, JSON.stringify({ ...data, testSnapshot: label }));
    const snapshot = await buildRecipePwa(pathToFileURL(`${directory}/`));
    snapshots.push({ directory, ...snapshot });
    const firstWorker = await readFile(`${directory}${recipeRoute}service-worker.js`, 'utf8');
    await buildRecipePwa(pathToFileURL(`${directory}/`));
    assert.equal(await readFile(`${directory}${recipeRoute}service-worker.js`, 'utf8'), firstWorker);
    assert.deepEqual(snapshot.urls, [...snapshot.urls].sort());
  }
  assert.notEqual(snapshots[0].cache, snapshots[1].cache);
  server = createServer(async (request, response) => {
    const url = new URL(request.url, 'http://localhost');
    const servingRoot = snapshots[version - 1].directory;
    const path = resolve(servingRoot, `.${url.pathname}${url.pathname.endsWith('/') ? 'index.html' : ''}`);
    if (!path.startsWith(`${servingRoot}/`)) { response.writeHead(403).end(); return; }
    if (failDownload && url.pathname === '/recipes-pwa/icon-512.png') { response.writeHead(503).end(); return; }
    try {
      let body = await readFile(path);
      const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.webp': 'image/webp', '.ico': 'image/x-icon', '.woff2': 'font/woff2' };
      response.writeHead(200, { 'Content-Type': types[extname(path)] ?? 'text/plain', 'Cache-Control': 'no-store' }).end(body);
    } catch { response.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch();
});
after(async () => { await browser?.close(); await new Promise(resolve => server?.close(resolve)); await rm(fixture, { recursive: true, force: true }); });

for (const [name, viewport] of [['desktop', { width: 1280, height: 900 }], ['mobile', { width: 390, height: 844 }]]) {
  test(`Recipe PWA installs and cooking tools work offline on ${name}`, { timeout: 60000 }, async () => {
    const context = await browser.newContext({ viewport });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(String(error)));
    page.on('console', message => { if (['warning', 'error'].includes(message.type())) errors.push(message.text()); });
    try {
      await page.goto(`${origin}${recipeRoute}`);
      await page.getByText('Recipes saved for offline use.', { exact: false }).waitFor();
      await page.waitForFunction(() => navigator.serviceWorker.controller);
      const metadata = await page.evaluate(async () => {
        const manifest = await fetch(document.querySelector('link[rel="manifest"]').href).then(r => r.json());
        const registration = await navigator.serviceWorker.getRegistration();
        return { manifest, scope: registration.scope };
      });
      assert.equal(metadata.manifest.scope, recipeRoute);
      assert.equal(metadata.manifest.start_url, recipeRoute);
      assert.equal(metadata.manifest.display, 'standalone');
      assert.equal(metadata.scope, `${origin}${recipeRoute}`);
      for (const icon of metadata.manifest.icons) {
        assert.equal(await page.evaluate(async url => (await fetch(url)).status, icon.src), 200);
      }
      await context.setOffline(true);
      await page.reload();
      await page.getByText('You are offline.', { exact: false }).waitFor();
      await page.getByRole('combobox', { name: 'Adult servings', exact: true }).selectOption('2');
      await page.getByRole('combobox', { name: 'Measurements', exact: true }).selectOption('metric');
      await page.getByRole('searchbox', { name: 'Search meals or ingredients' }).fill('salmon');
      await page.waitForFunction(() => document.querySelectorAll('.recipe-card').length === 1);
      await page.getByRole('checkbox', { name: /Add to plan/ }).check();
      assert.ok(await page.locator('.groceries li').count() > 0);
      await page.getByRole('button', { name: /See recipe/ }).click();
      await page.getByRole('button', { name: 'Cooking view', exact: true }).click();
      assert.ok(await page.locator('.recipe-detail').isVisible());
      assert.ok(await page.locator('.recipe-detail .trn-table').count() > 0);
      await page.waitForFunction(() => [...document.querySelectorAll('.recipe-detail img')].every(image => image.complete && image.naturalWidth > 0));
      await page.getByRole('button', { name: 'Exit cooking view', exact: true }).click();
      assert.equal(await page.evaluate(async () => (await fetch('/data/recipe-library.json')).status), 200);
      assert.equal(await page.evaluate(async () => (await fetch('/data/recipe-library.md')).status), 200);
      await page.emulateMedia({ media: 'print' });
      assert.equal(await page.locator('.recipe-pwa').isVisible(), false);
      await page.emulateMedia({ media: 'screen' });
      if (process.env.PWA_SCREENSHOTS) {
        await mkdir('.migration-work/pwa', { recursive: true });
        await page.screenshot({ path: `.migration-work/pwa/${name}-offline.png`, fullPage: true });
        await page.getByRole('button', { name: '← Back to dinners', exact: true }).click();
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({ path: `.migration-work/pwa/${name}.png` });
      }
      // Changing the recipe URL's query or fragment still opens the cached app.
      await page.goto(`${origin}${recipeRoute}?cooking=1#shopping-list`);
      await page.getByRole('combobox', { name: 'Adult servings', exact: true }).waitFor();
      assert.equal(await page.getByRole('combobox', { name: 'Adult servings', exact: true }).inputValue(), '2');
      assert.deepEqual(errors, []);
      await context.setOffline(false);
      await page.goto(`${origin}/`);
      assert.equal(await page.evaluate(() => navigator.serviceWorker.controller), null);
    } finally { await context.close(); }
  });
}

test('Distinct snapshot update waits for both tabs, then serves new recipes offline', { timeout: 60000 }, async () => {
  version = 1;
  const context = await browser.newContext();
  const snapshotLabel = page => page.locator('meta[name="pwa-test-snapshot"]').getAttribute('content');
  try {
    const tabs = [await context.newPage(), await context.newPage()];
    for (const page of tabs) {
      await page.goto(`${origin}${recipeRoute}`);
      await page.getByText('Recipes saved for offline use.', { exact: false }).waitFor();
      assert.equal(await snapshotLabel(page), 'A');
    }
    version = 2;
    await tabs[0].evaluate(async () => { const registration = await navigator.serviceWorker.getRegistration(); await registration.update(); });
    await tabs[0].getByText('Updated recipes are downloaded.', { exact: false }).waitFor();
    await context.setOffline(true);
    for (const page of tabs) {
      await page.reload();
      assert.equal(await snapshotLabel(page), 'A');
      assert.equal(await page.evaluate(async () => (await fetch('/data/recipe-library.json')).json().then(data => data.testSnapshot)), 'A');
    }
    await tabs[0].close();
    assert.equal(await tabs[1].evaluate(async () => (await navigator.serviceWorker.getRegistration()).waiting.state), 'installed');
    assert.ok((await tabs[1].evaluate(() => caches.keys())).includes(snapshots[0].cache));
    await tabs[1].close();
    const reopened = await context.newPage();
    // Wait for activation without relying on a network visit to establish it.
    await reopened.goto(`${origin}${recipeRoute}`);
    await reopened.waitForFunction(async () => !(await navigator.serviceWorker.getRegistration()).waiting);
    await reopened.reload();
    assert.equal(await snapshotLabel(reopened), 'B');
    assert.equal(await reopened.evaluate(async () => (await fetch('/data/recipe-library.json')).json().then(data => data.testSnapshot)), 'B');
    assert.deepEqual(await reopened.evaluate(() => caches.keys()), [snapshots[1].cache]);
    await reopened.getByRole('combobox', { name: 'Adult servings', exact: true }).selectOption('6');
  } finally { await context.close(); }
});

test('Failed replacement preserves the previous offline snapshot and reports failure', { timeout: 60000 }, async () => {
  version = 1;
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    await page.goto(`${origin}${recipeRoute}`);
    await page.getByText('Recipes saved for offline use.', { exact: false }).waitFor();
    version = 2;
    failDownload = true;
    await page.evaluate(async () => { const registration = await navigator.serviceWorker.getRegistration(); await registration.update(); });
    await page.getByText('Update download failed.', { exact: false }).waitFor();
    await context.setOffline(true);
    await page.reload();
    await page.getByText('You are offline.', { exact: false }).waitFor();
    assert.equal(await page.locator('meta[name="pwa-test-snapshot"]').getAttribute('content'), 'A');
    assert.equal(await page.evaluate(async () => (await fetch('/data/recipe-library.json')).json().then(data => data.testSnapshot)), 'A');
    await page.getByRole('combobox', { name: 'Adult servings', exact: true }).selectOption('2');
    assert.equal(await page.evaluate(async () => (await navigator.serviceWorker.getRegistration()).waiting), null);
  } finally { failDownload = false; await context.close(); }
});

test('Failed first download does not claim offline readiness', { timeout: 60000 }, async () => {
  failDownload = true;
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    await page.goto(`${origin}${recipeRoute}`);
    await page.getByText('Recipes could not be saved offline.', { exact: false }).waitFor();
    assert.equal(await page.evaluate(() => navigator.serviceWorker.controller), null);
  } finally { failDownload = false; await context.close(); }
});
