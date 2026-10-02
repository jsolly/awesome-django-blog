import { blogContent, site } from '../lib/content';
import { xml } from '../lib/html';
export async function GET() {
  const { posts, categories } = await blogContent();
  const paths = ['/', '/all-posts/', '/privacy/', '/works-cited/'];
  const entries = [
    ...paths.map(path => `<url><loc>${site}${path}</loc></url>`),
    ...categories.map(({ data }) => `<url><loc>${site}/category/${data.slug}/</loc></url>`),
    ...posts.map(({ data }) => `<url><loc>${xml(`${site}/post/${data.slug}/`)}</loc><lastmod>${data.updated.toISOString()}</lastmod></url>`),
  ];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${entries.join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
