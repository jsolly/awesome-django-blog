import assert from 'node:assert/strict';
import test from 'node:test';
import { chromium } from 'playwright';
import { productionUrl, smoke, verifyRelease, verifyFeeds, verifyCanonicalRoutes } from './production-smoke-scenario.mjs';
import historicalRedirects from '../src/content/redirects.json' with { type: 'json' };
import migrationReceipt from '../src/content/migration-receipt.json' with { type: 'json' };
import { runSmoke } from './production-smoke.mjs';

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


test('public article, GET search, feeds and mobile navigation are read-only', async () => {
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    const checked = [];
    await context.route('**/*', route => {
      const url = new URL(route.request().url());
      assert.equal(route.request().method(), 'GET');
      const body = url.pathname === '/'
        ? '<h1>Latest Posts!</h1><a class="post-card-link" href="/post/example/">Example post</a><button aria-expanded="false" onclick="this.setAttribute(\'aria-expanded\',\'true\')">Menu</button><nav aria-label="Main navigation"><a href="/all-posts/">All posts</a></nav><footer><nav aria-label="Footer"><a href="/all-posts/">All posts</a></nav></footer>'
        : url.pathname === '/post/example/'
          ? '<article><h1>Example post</h1><div class="post-text">Public article content</div></article>'
          : url.pathname === '/all-posts/'
            ? '<h1>All Posts!</h1><form action="/search/" method="get"><input type="search" name="searched" aria-label="Search"></form>'
            : "<h1>You searched for 'Example post'</h1><a class=\"post-card-link\" href=\"/post/example/\">Example post</a>";
      return route.fulfill({ contentType: 'text/html', body });
    });
    await page.goto(productionUrl);
    await smoke({ page, verifyHttp: async url => {
      checked.push(url);
      const atom = new URL(url).pathname.replace(/\/$/u, '') === '/atom';
      const response = new Response(atom ? '<feed></feed>' : '<rss></rss>', { headers: { 'content-type': atom ? 'application/atom+xml' : 'application/rss+xml' } });
      const rule = historicalRedirects.find(rule => rule.source.replace(/\/$/u, '') === new URL(url).pathname.replace(/\/$/u, ''));
      const finalPath = rule ? `${rule.destination.replace(/\/$/u, '')}/` : new URL(url).pathname === '/post/example' ? '/post/example/' : new URL(url).pathname;
      Object.defineProperty(response, 'url', { value: `${productionUrl}${finalPath}` });
      return response;
    } });
    assert.deepEqual(checked, [
      `${productionUrl}/post/example/`,
      `${productionUrl}/post/example`,
      ...historicalRedirects.filter(rule => migrationReceipt.publishedPaths.includes(`${rule.destination.replace(/\/$/u, '')}/`)).flatMap(rule => [`${productionUrl}${rule.source.replace(/\/$/u, '')}`, `${productionUrl}${rule.source.replace(/\/$/u, '')}/`]),
      `${productionUrl}/search/?searched=Example+post`,
      `${productionUrl}/rss`,
      `${productionUrl}/rss/`,
      `${productionUrl}/atom`,
      `${productionUrl}/atom/`,
    ]);
  } finally {
    await browser.close();
  }
});

test('release readiness rejects stale builds before launching a browser', async () => {
  const sha = 'a'.repeat(40);
  await verifyRelease({ releaseSha: sha, verifyHttp: async () => Response.json({ sha }) });
  await assert.rejects(verifyRelease({ releaseSha: sha, verifyHttp: async () => Response.json({ sha: 'b'.repeat(40) }) }), /intended release/u);
  let launched = false;
  const receipt = await runSmoke({
    scenario: { productionUrl, verifyRelease, smoke },
    env: { PRODUCTION_SMOKE_RELEASE_SHA: sha, PRODUCTION_SMOKE_REQUEST_ID: 'stale-release-contract' },
    readinessMs: 0,
    fetcher: async url => {
      const response = Response.json({ sha: 'b'.repeat(40) });
      Object.defineProperty(response, 'url', { value: url });
      return response;
    },
    launch: async () => { launched = true; throw new Error('Must not launch'); },
  });
  assert.equal(receipt.success, false);
  assert.equal(launched, false);
  assert.ok(receipt.errors.some(error => error.includes('Readiness deadline')));
});

test('feed smoke rejects a successful HTML response in place of XML', async () => {
  await assert.rejects(verifyFeeds({ verifyHttp: async () => new Response('<html></html>', { headers: { 'content-type': 'text/html' } }) }), /XML feed MIME/u);
});

test('canonical route smoke rejects broken and misdirected historical links', async () => {
  const routes = [{ source: '/post/example', destination: '/post/example/' },
    ...historicalRedirects.filter(rule => migrationReceipt.publishedPaths.includes(`${rule.destination.replace(/\/$/u, '')}/`)).flatMap(rule => [
      { source: rule.source.replace(/\/$/u, ''), destination: `${rule.destination.replace(/\/$/u, '')}/` },
      { source: `${rule.source.replace(/\/$/u, '')}/`, destination: `${rule.destination.replace(/\/$/u, '')}/` },
    ])];
  for (const broken of routes) {
    for (const failure of ['404', 'wrong destination']) {
      const checked = [];
      await assert.rejects(verifyCanonicalRoutes({ postPath: '/post/example/', verifyHttp: async url => {
        const path = new URL(url).pathname;
        checked.push(path);
        const route = routes.find(route => route.source === path);
        assert.ok(route, 'Unexpected smoke request');
        const inject = path === broken.source;
        const response = new Response('', { status: inject && failure === '404' ? 404 : 200 });
        Object.defineProperty(response, 'url', { value: `${productionUrl}${inject && failure === 'wrong destination' ? '/post/wrong/' : route.destination}` });
        return response;
      } }), failure === '404' ? /route is readable/u : /reaches its canonical article/u);
      assert.ok(checked.includes(broken.source), `Failure fixture reached ${broken.source}`);
    }
  }
});
