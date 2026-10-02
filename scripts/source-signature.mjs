import assert from 'node:assert/strict';
import { load } from 'cheerio';
import { articleSignature } from './article-signature.mjs';

const recipeStyles = '#content-area,#main{min-width:0;}@media(max-width:1239px){.container{grid-template-columns:minmax(0,1fr);}}article.media,article.media>.media-body{min-width:0;max-width:100%;width:100%}';

// Source-only oracle: never call the application's sanitizer, converter or
// heading helper. These are the explicitly permitted migration transformations.
export function sourceSignature(html, slug) {
  const $ = load(html, {}, false);
  assert.equal($('script').length, 0, `Unaccounted executable content: ${slug}`);
  for (const style of $('style').toArray()) {
    assert.equal(slug, '15-minute-dump-and-go-instant-pot-recipes', 'Unaccounted authored stylesheet');
    assert.equal($(style).text(), recipeStyles, 'Authored stylesheet changed; reconcile bundled article-content.css');
  }
  $('style').remove();
  $('h1,h2,h3').each((_i, node) => {
    // Verified against the former static/js/addHeaderIdsAndLinks.js.
    $(node).attr('id', $(node).text().trim().toLowerCase().replace(/\s+/gu, '-').replace(/[^a-zA-Z0-9_-]/gu, ''));
  });
  $('img').each((_i, node) => {
    const path = $(node).attr('src') ?? '';
    if (!/^https:\/\//u.test(path) && !path.startsWith('/media/')) $(node).attr('src', path === 'default.webp' ? '/media/default.webp' : `https://d1d7p8ufhgz4ld.cloudfront.net/media/${path.replace(/^\/?mediafiles\//u, '')}`);
  });
  $('iframe').each((_i, node) => { if (!$(node).attr('title')) $(node).attr('title', 'Embedded article content'); });
  return articleSignature($.html());
}
