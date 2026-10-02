import { blogContent } from '../lib/content';
import { plainText } from '../lib/html';
export async function GET() { const { posts } = await blogContent(); return Response.json(posts.map(({ data, html }) => ({ slug: data.slug, title: data.title, description: data.description, text: plainText(html) }))); }
