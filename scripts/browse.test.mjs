import { before, after, test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { resolve, extname } from 'node:path';
import { chromium } from 'playwright';

const origin = 'http://blog.test';
const dist = resolve('dist');
let browser;
before(async () => { browser = await chromium.launch(); });
after(async () => { await browser?.close(); });

// Serve the real built pages and modules, with article imagery isolated from network availability.
async function openPage({ observer = true } = {}) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  if (!observer) await context.addInitScript(() => { delete window.IntersectionObserver; });
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) return route.fulfill({ contentType: 'image/svg+xml', body: '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" />' });
    const path = resolve(dist, `.${url.pathname}${url.pathname.endsWith('/') ? 'index.html' : ''}`);
    assert.ok(path.startsWith(`${dist}/`));
    const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };
    try { return route.fulfill({ contentType: types[extname(path)] ?? 'application/octet-stream', body: await readFile(path) }); }
    catch (error) { if (error.code !== 'ENOENT') throw error; return route.fulfill({ status: 404 }); }
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(String(error)));
  page.setDefaultTimeout(5000);
  return { context, page, errors };
}
async function navigate(page, path = '/') {
  await page.goto(`${origin}${path}`, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => !document.querySelector('.menu-toggle').disabled);
}
async function countIs(page, count) {
  await page.waitForFunction(expected => document.querySelectorAll('.post-card').length === expected, count);
}
async function appendByScrolling(page, count) {
  await page.locator('.load-more').scrollIntoViewIfNeeded();
  await countIs(page, count);
}

test('Scrolling pauses, keyboard loading resumes, and returning preserves the loaded articles', { timeout: 30000 }, async () => {
  const { context, page, errors } = await openPage();
  try {
    await navigate(page);
    await countIs(page, 3);
    const expected = await page.locator('.post-card-link').evaluateAll(links => links.map(link => link.getAttribute('href')));
    for (const count of [6, 9, 12]) await appendByScrolling(page, count);
    await page.locator('.load-more').scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await countIs(page, 12);
    assert.equal(await page.locator('.load-more-button.paused').count(), 1);
    const more = page.getByRole('link', { name: 'Load more posts', exact: true });
    await more.focus();
    await page.keyboard.press('Enter');
    await countIs(page, 15);
    await page.waitForFunction(() => document.activeElement === document.querySelectorAll('.post-card-link')[12]);
    for (const count of [18, 21, 24]) await appendByScrolling(page, count);
    await page.locator('.load-more').scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    await countIs(page, 24);
    const links = await page.locator('.post-card-link').evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
    assert.equal(new Set(links).size, 24);
    assert.deepEqual(links.slice(0, 3), expected);
    const target = page.locator('.post-card-link').nth(5);
    const href = await target.getAttribute('href');
    await target.click();
    await page.waitForURL(`${origin}${href}`);
    await page.goBack({ waitUntil: 'domcontentloaded' });
    await countIs(page, 24);
    await navigate(page, '/?page=3');
    await countIs(page, 9);
    await navigate(page, '/?page=999');
    const count = await page.locator('.post-card').count();
    assert.ok(count > 24);
    assert.equal(await page.getByRole('link', { name: 'Load more posts', exact: true }).count(), 0);
    assert.ok((await page.locator('.load-more').innerText()).includes("You've reached the end"));
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});

test('Manual loading remains usable without IntersectionObserver', async () => {
  const { context, page, errors } = await openPage({ observer: false });
  try {
    await navigate(page);
    await countIs(page, 3);
    await page.getByRole('link', { name: 'Load more posts', exact: true }).click();
    await countIs(page, 6);
    assert.equal(new URL(page.url()).searchParams.get('page'), '2');
    assert.deepEqual(errors, []);
  } finally { await context.close(); }
});
