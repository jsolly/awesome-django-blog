import { site } from '../lib/content';
export function GET() { return new Response(`User-agent: *\nAllow: /\nDisallow: /search/\nSitemap: ${site}/sitemap.xml\n`, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } }); }
