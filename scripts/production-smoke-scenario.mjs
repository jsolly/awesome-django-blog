import assert from 'node:assert/strict';
import historicalRedirects from '../src/content/redirects.json' with { type: 'json' };
import migrationReceipt from '../src/content/migration-receipt.json' with { type: 'json' };

export const productionUrl = 'https://www.blogthedata.com';

export async function verifyRelease({ verifyHttp, releaseSha }) {
  const response = await verifyHttp(`${productionUrl}/release.json`);
  assert.equal((await response.json()).sha, releaseSha, 'Canonical site must serve the intended release');
}

export async function verifyFeeds({ verifyHttp }) {
  for (const [path, mime, root] of [['rss', 'application/rss+xml', '<rss'], ['atom', 'application/atom+xml', '<feed']]) {
    for (const suffix of ['', '/']) {
      const response = await verifyHttp(`${productionUrl}/${path}${suffix}`);
      assert.ok(response.headers.get('content-type')?.startsWith(mime), `${path} has XML feed MIME type`);
      assert.ok((await response.text()).includes(root), `${path} serves a feed document`);
    }
  }
}

export async function verifyCanonicalRoutes({ verifyHttp, postPath }) {
  // The frozen closed-loop alias already targets a missing article. The build
  // contract pins that sole documented exception; do not invent replacement content.
  const readableAliases = historicalRedirects.filter(rule => migrationReceipt.publishedPaths.includes(`${rule.destination.replace(/\/$/u, '')}/`));
  const routes = [{ source: postPath.slice(0, -1), destination: postPath }, ...readableAliases.flatMap(rule => {
    const source = rule.source.replace(/\/$/u, '');
    const destination = `${rule.destination.replace(/\/$/u, '')}/`;
    return [{ source, destination }, { source: `${source}/`, destination }];
  })];
  for (const route of routes) {
    const response = await verifyHttp(`${productionUrl}${route.source}`);
    assert.equal(response.status, 200, `Historical/bare article route is readable: ${route.source}`);
    assert.equal(response.url, `${productionUrl}${route.destination}`, `Historical/bare article route reaches its canonical article: ${route.source}`);
  }
}

export async function smoke({ page, verifyHttp, artifacts }) {
  await page.getByRole('heading', { name: 'Latest Posts!', exact: true }).waitFor();
  const post = page.locator('a.post-card-link').first();
  const title = (await post.textContent()).trim();
  const postPath = await post.getAttribute('href');
  assert.match(postPath, /^\/post\/[^/]+\/$/, 'home links to a public article');
  await post.click();
  await page.waitForURL(new URL(postPath, productionUrl).href);
  assert.equal(await page.locator('article h1').evaluate(heading => [...heading.childNodes].filter(node => node.nodeType === Node.TEXT_NODE).map(node => node.textContent).join('').trim()), title, 'article title matches the selected post');
  assert.ok((await page.locator('article .post-text').textContent()).trim().length > 0, 'article body is not empty');
  await verifyHttp(new URL(postPath, productionUrl).href);
  await verifyCanonicalRoutes({ verifyHttp, postPath });
  await page.goto(`${productionUrl}/all-posts/`);
  await page.getByRole('heading', { name: 'All Posts!', exact: true }).waitFor();
  await page.getByRole('searchbox', { name: 'Search', exact: true }).fill(title);
  await page.getByRole('searchbox', { name: 'Search', exact: true }).press('Enter');
  await page.waitForURL(url => url.pathname === '/search/' && url.searchParams.get('searched') === title);
  await page.getByRole('heading', { name: `You searched for '${title}'`, exact: true }).waitFor();
  const result = page.locator('a.post-card-link').filter({ hasText: title }).first();
  await result.waitFor();
  assert.equal(await result.getAttribute('href'), postPath, 'search finds the article just read');
  await verifyHttp(page.url());
  await verifyFeeds({ verifyHttp });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(productionUrl);
  const menu = page.getByRole('button', { name: 'Open menu', exact: true });
  await menu.click();
  const closeMenu = page.getByRole('button', { name: 'Close menu', exact: true });
  assert.equal(await closeMenu.getAttribute('aria-expanded'), 'true', 'Mobile menu opens');
  await closeMenu.click();
  assert.equal(await menu.getAttribute('aria-expanded'), 'false', 'Mobile menu closes');
  await menu.click();
  await page.getByRole('navigation', { name: 'Main navigation' }).getByRole('link', { name: 'All posts', exact: true }).click();
  await page.waitForURL(`${productionUrl}/all-posts/`);
  if (artifacts) await page.screenshot({ path: `${artifacts}/mobile.png`, fullPage: true });
}
