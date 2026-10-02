import { feed } from '../../lib/feeds';
export async function GET() { return new Response(await feed('rss'), { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } }); }
