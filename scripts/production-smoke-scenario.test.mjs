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


test('public article and GET search verify their HTTP responses without release headers', async () => {
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    const checked = [];
    await context.route('**/*', route => {
      const url = new URL(route.request().url());
      assert.equal(route.request().method(), 'GET');
      const body = url.pathname === '/'
        ? '<h1>Latest Posts!</h1><a class="post-card-link" href="/post/example/">Example post</a>'
        : url.pathname === '/post/example/'
          ? '<article><h1>Example post</h1><div class="post-text">Public article content</div></article>'
          : url.pathname === '/all-posts/'
            ? '<h1>All Posts!</h1><form action="/search/" method="get"><input type="search" name="searched" aria-label="Search"></form>'
            : "<h1>You searched for 'Example post'</h1><a class=\"post-card-link\" href=\"/post/example/\">Example post</a>";
      return route.fulfill({ contentType: 'text/html', body });
    });
    await page.goto(productionUrl);
    await smoke({ page, verifyHttp: async url => { checked.push(url); } });
    assert.deepEqual(checked, [
      `${productionUrl}/post/example/`,
      `${productionUrl}/search/?searched=Example+post`,
    ]);
  } finally {
    await browser.close();
  }
});
