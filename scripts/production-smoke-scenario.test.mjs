import assert from 'node:assert/strict';
import test from 'node:test';
import { chromium } from 'playwright';
import { productionUrl, smoke } from './production-smoke-scenario.mjs';

test('an article page with no article body fails the public reading smoke', async () => {
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    page.setDefaultTimeout(300);
    await context.route('**/*', route => route.fulfill({
      contentType: 'text/html',
      body: new URL(route.request().url()).pathname === '/'
        ? '<h1>Latest Posts!</h1><a class="post-card-link" href="/post/example/">Example post</a>'
        : '<article><h1>Example post</h1><div class="post-text"></div></article>',
    }));
    await page.goto(productionUrl);
    await assert.rejects(smoke({ page, context }), /article body is not empty/);
  } finally {
    await browser.close();
  }
});
