import { feed } from '../../lib/feeds';
export async function GET() { return new Response(await feed('atom'), { headers: { 'Content-Type': 'application/atom+xml; charset=utf-8' } }); }
