import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { convertExport } from './import-django.mjs';
import { parsePost } from './content-files.mjs';
import { articleSignature } from './article-signature.mjs';
import { sourceSignature } from './source-signature.mjs';
import { load } from 'cheerio';

const sourcePath = process.argv[2];
if (!sourcePath) throw new Error('Usage: node scripts/verify-migration.mjs <authoritative-dumpdata.json>');
const records = JSON.parse(await readFile(sourcePath, 'utf8'));
const { posts, categories, redirects } = convertExport(records);
for (const [name, entries, extension] of [['posts', posts, 'md'], ['categories', categories, 'json']]) {
  assert.deepEqual((await readdir(`src/content/${name}`)).filter(file => file.endsWith(`.${extension}`)).sort(), entries.map(entry => `${entry.slug}.${extension}`).sort(), `Unexpected or missing ${name}`);
}
assert.deepEqual(JSON.parse(await readFile('src/content/redirects.json', 'utf8')), redirects);
const config = JSON.parse(await readFile('vercel.json', 'utf8'));
for (const redirect of redirects) {
  assert.ok(config.redirects.some(rule => rule.source === redirect.source && rule.destination === redirect.destination && rule.permanent), `Missing Vercel redirect: ${redirect.source}`);
}
for (const [name, entries] of [['posts', posts], ['categories', categories]]) {
  for (const entry of entries) {
    const actual = name === 'posts' ? parsePost(await readFile(`src/content/posts/${entry.slug}.md`, 'utf8')) : JSON.parse(await readFile(`src/content/categories/${entry.slug}.json`, 'utf8'));
    assert.deepEqual(actual, entry, `Source parity failed: ${name}/${entry.slug}`);
  }
}
// Compare directly with the raw source too. The importer cannot be its own oracle.
const rawPosts = records.filter(row => row.model === 'blog.post');
const rawPostsById = new Map(rawPosts.map(row => [row.pk, row]));
const rawSimilarities = records.filter(row => row.model === 'blog.similarity');
const rawFieldMap = {
  title: 'title', slug: 'slug', metadesc: 'description', draft: 'draft',
  metaimg: 'legacyImage', metaimg_width: 'imageWidth', metaimg_height: 'imageHeight',
  metaimg_alt_txt: 'imageAlt', metaimg_attribution: 'imageAttribution',
  snippet: 'excerpt', date_posted: 'published', date_updated: 'updated',
  author: 'legacyAuthorId',
};
for (const row of rawPosts) {
  const actual = parsePost(await readFile(`src/content/posts/${row.fields.slug}.md`, 'utf8'));
  assert.deepEqual(Object.keys(row.fields).sort(), [...Object.keys(rawFieldMap), 'category', 'content'].sort(), `Unmapped source field: ${row.fields.slug}`);
  for (const [rawName, destinationName] of Object.entries(rawFieldMap)) {
    const expected = ['metadesc', 'metaimg_attribution'].includes(rawName) ? row.fields[rawName] ?? '' : row.fields[rawName];
    assert.deepEqual(actual[destinationName], expected, `Raw source mismatch ${row.fields.slug}.${rawName}`);
  }
  assert.equal(actual.category, records.find(category => category.model === 'blog.category' && category.pk === row.fields.category).fields.slug);
  const related = rawSimilarities.filter(similarity => similarity.fields.post1 === row.pk)
    .toSorted((a, b) => b.fields.score - a.fields.score).slice(0, 3).map(similarity => {
      const target = rawPostsById.get(similarity.fields.post2);
      assert.ok(target, `Unknown related source post: ${similarity.fields.post2}`);
      return target;
    });
  assert.deepEqual(actual.related, related.map(target => target.fields.slug), `Raw related associations mismatch: ${actual.slug}`);
  if (!actual.draft) {
    const $ = load(await readFile(`dist/post/${actual.slug}/index.html`, 'utf8'));
    assert.equal($('.article-body').length, 1, `Missing article body: ${actual.slug}`);
    const expected = sourceSignature(row.fields.content, actual.slug);
    const rendered = articleSignature($('.article-body').html());
    for (const [part, value] of Object.entries(expected)) assert.deepEqual(rendered[part], value, `Rendered ${part} mismatch: ${actual.slug}`);
    const relatedLinks = $('.related-posts a.post-card-link').toArray().map(link => $(link).attr('href')).sort();
    assert.deepEqual(relatedLinks, related.filter(target => !target.fields.draft).map(target => `/post/${target.fields.slug}/`).sort(), `Rendered related associations mismatch: ${actual.slug}`);
  }
}
const feedSource = rawPosts.filter(row => !row.fields.draft)
  .toSorted((a, b) => Date.parse(b.fields.date_updated) - Date.parse(a.fields.date_updated) || Date.parse(b.fields.date_posted) - Date.parse(a.fields.date_posted)).slice(0, 5);
const rss = load(await readFile('dist/rss', 'utf8'), { xml: true });
const atom = load(await readFile('dist/atom', 'utf8'), { xml: true });
assert.deepEqual(rss('item').toArray().map(item => ({ title: rss(item).find('title').text(), link: rss(item).find('link').text(), guid: rss(item).find('guid').text(), description: rss(item).find('description').text() })), feedSource.map(row => ({ title: row.fields.title, link: `https://www.blogthedata.com/post/${row.fields.slug}/`, guid: `https://www.blogthedata.com/post/${row.fields.slug}/`, description: row.fields.metadesc ?? '' })));
assert.deepEqual(atom('entry').toArray().map(entry => ({ title: atom(entry).find('title').text(), link: atom(entry).find('link').attr('href'), id: atom(entry).find('id').text(), updated: atom(entry).find('updated').text(), author: atom(entry).find('author name').text() })), feedSource.map(row => ({ title: row.fields.title, link: `https://www.blogthedata.com/post/${row.fields.slug}/`, id: `https://www.blogthedata.com/post/${row.fields.slug}/`, updated: new Date(row.fields.date_posted).toISOString(), author: 'John_Solly' })));
process.stdout.write(`Verified source parity for ${posts.length} posts, ${categories.length} categories and ${redirects.length} redirects.\n`);
