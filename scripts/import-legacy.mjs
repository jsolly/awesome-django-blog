import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { serializePost } from './content-files.mjs';
import { htmlToMarkdown } from './html-to-markdown.mjs';

const slugPattern = /^[A-Za-z0-9_-]+$/u;

export function convertExport(records) {
  if (!Array.isArray(records)) throw new Error('Expected a legacy export record array');
  const categories = records.filter(row => row.model === 'blog.category').map(row => ({
    slug: row.fields.slug, name: row.fields.name, description: row.fields.description,
    legacyId: row.pk,
  }));
  const byId = new Map(categories.map(category => [category.legacyId, category.slug]));
  const posts = records.filter(row => row.model === 'blog.post').map(row => {
    const source = row.fields;
    const category = byId.get(source.category);
    if (!category) throw new Error(`Unknown category for ${source.slug}`);
    for (const name of ['date_posted', 'date_updated']) {
      if (!Number.isFinite(Date.parse(source[name]))) throw new Error(`Invalid ${name} for ${source.slug}`);
    }
    if (typeof source.content !== 'string' || !source.content.trim()) throw new Error(`Missing body for ${source.slug}`);
    if (typeof source.title !== 'string' || !source.title.trim()) throw new Error(`Missing title for ${source.slug}`);
    if (typeof source.draft !== 'boolean') throw new Error(`Missing draft state for ${source.slug}`);
    if (source.author !== 2) throw new Error(`Unknown public author ${source.author} for ${source.slug}. Add an explicit verified author mapping before import.`);
    return {
      slug: source.slug, title: source.title, category, description: source.metadesc ?? '',
      draft: source.draft,
      image: source.metaimg === 'default.webp' ? '/media/default.webp' : `https://d1d7p8ufhgz4ld.cloudfront.net/media/${source.metaimg}`,
      legacyImage: source.metaimg, imageAlt: source.metaimg_alt_txt,
      imageAttribution: source.metaimg_attribution ?? '',
      imageWidth: source.metaimg_width, imageHeight: source.metaimg_height,
      published: source.date_posted, updated: source.date_updated,
      author: 'John Solly', feedAuthor: 'John_Solly', legacyAuthorId: source.author,
      body: htmlToMarkdown(source.content), excerpt: source.snippet ?? '', legacyId: row.pk,
    };
  });
  const byPostId = new Map(posts.map(post => [post.legacyId, post.slug]));
  const similarities = records.filter(row => row.model === 'blog.similarity');
  for (const post of posts) {
    post.related = similarities.filter(row => row.fields.post1 === post.legacyId)
      .sort((a, b) => b.fields.score - a.fields.score).slice(0, 3)
      .map(row => byPostId.get(row.fields.post2)).filter(Boolean);
  }
  for (const [name, entries] of [['categories', categories], ['posts', posts]]) {
    const slugs = new Set();
    for (const entry of entries) {
      if (!slugPattern.test(entry.slug)) throw new Error(`Unsafe ${name} slug: ${entry.slug}`);
      if (slugs.has(entry.slug)) throw new Error(`Duplicate ${name} slug: ${entry.slug}`);
      slugs.add(entry.slug);
    }
  }
  if (!posts.length || !categories.length) throw new Error('Export has no posts or categories');
  const redirectRows = records.filter(row => row.model === 'redirects.redirect');
  const publicSite = records.find(row => row.model === 'sites.site' && row.fields.domain === 'www.blogthedata.com');
  if (redirectRows.length && !publicSite) throw new Error('Redirect export needs the canonical public site');
  const redirects = redirectRows.filter(row => row.fields.site === publicSite.pk).map(row => {
    for (const path of [row.fields.old_path, row.fields.new_path]) {
      if (typeof path !== 'string' || !/^\/(?!\/)[A-Za-z0-9/_-]+$/u.test(path)) throw new Error(`Unsupported redirect path: ${path}`);
    }
    return { source: row.fields.old_path, destination: row.fields.new_path, legacyId: row.pk };
  });
  if (new Set(redirects.map(redirect => redirect.source)).size !== redirects.length) throw new Error('Duplicate redirect source');
  return { categories, posts, redirects };
}

export async function importExport({ sourcePath, destination }) {
  const source = await readFile(sourcePath, 'utf8');
  const { categories, posts, redirects } = convertExport(JSON.parse(source));
  await mkdir(destination, { recursive: true });
  const existing = await readdir(destination);
  if (existing.length) throw new Error('Destination must be empty. Import into a new directory to compare with CMS edits.');
  for (const [name, entries] of [['categories', categories], ['posts', posts]]) {
    await mkdir(resolve(destination, name));
    for (const entry of entries) {
      const filename = `${entry.slug}.${name === 'posts' ? 'md' : 'json'}`;
      await writeFile(resolve(destination, name, filename), name === 'posts' ? serializePost(entry) : `${JSON.stringify(entry, null, 2)}\n`);
    }
  }
  const receipt = {
    sourceSha256: createHash('sha256').update(source).digest('hex'),
    posts: posts.length, drafts: posts.filter(post => post.draft).length, categories: categories.length,
    redirects: redirects.length,
    publishedPaths: posts.filter(post => !post.draft).map(post => `/post/${post.slug}/`).sort(),
    categoryPaths: categories.map(category => `/category/${category.slug}/`).sort(),
  };
  await writeFile(resolve(destination, 'redirects.json'), `${JSON.stringify(redirects, null, 2)}\n`);
  await writeFile(resolve(destination, 'migration-receipt.json'), `${JSON.stringify(receipt, null, 2)}\n`);
  return receipt;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const [, , sourcePath, destination] = process.argv;
  if (!sourcePath || !destination) throw new Error('Usage: node scripts/import-legacy.mjs <dumpdata.json> <empty-directory>');
  const receipt = await importExport({ sourcePath, destination: resolve(destination) });
  process.stdout.write(`Imported ${receipt.posts} posts and ${receipt.categories} categories.\n`);
}
