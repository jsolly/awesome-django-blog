import assert from 'node:assert/strict';

export const productionUrl = 'https://www.blogthedata.com';

export async function smoke({ page }) {
  await page.getByRole('heading', { name: 'Latest Posts!', exact: true }).waitFor();
  const post = page.locator('a.post-card-link').first();
  const title = (await post.textContent()).trim();
  const postPath = await post.getAttribute('href');
  assert.match(postPath, /^\/post\/[^/]+\/$/, 'home links to a public article');
  await post.click();
  await page.waitForURL(new URL(postPath, productionUrl).href);
  assert.equal(await page.locator('article h1').evaluate(heading => [...heading.childNodes].filter(node => node.nodeType === Node.TEXT_NODE).map(node => node.textContent).join('').trim()), title, 'article title matches the selected post');
  assert.ok((await page.locator('article .post-text').textContent()).trim().length > 0, 'article body is not empty');
  await page.goto(`${productionUrl}/all-posts/`);
  await page.getByRole('heading', { name: 'All Posts!', exact: true }).waitFor();
  await page.getByRole('searchbox', { name: 'Search', exact: true }).fill(title);
  await page.getByRole('searchbox', { name: 'Search', exact: true }).press('Enter');
  await page.waitForURL(url => url.pathname === '/search/' && url.searchParams.get('searched') === title);
  await page.getByRole('heading', { name: `You searched for '${title}'`, exact: true }).waitFor();
  const result = page.locator('a.post-card-link').filter({ hasText: title }).first();
  await result.waitFor();
  assert.equal(await result.getAttribute('href'), postPath, 'search finds the article just read');
}
