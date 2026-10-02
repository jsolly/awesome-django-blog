import { blogContent, site } from './content';
import { xml } from './html';

export async function feedPosts() {
  const { posts } = await blogContent();
  return posts.toSorted((a, b) => b.data.updated.getTime() - a.data.updated.getTime()).slice(0, 5);
}

export async function feed(kind: 'rss' | 'atom') {
  const posts = await feedPosts();
  const title = 'blogthedata | Blog';
  const description = 'Latest blog posts from blogthedata';
  const feedUrl = `${site}/${kind}/`;
  const items = posts.map(({ data }) => {
    const link = `${site}/post/${data.slug}/`;
    return kind === 'rss'
      ? `<item><title>${xml(data.title)}</title><link>${link}</link><description>${xml(data.description)}</description><guid>${link}</guid></item>`
      : `<entry><title>${xml(data.title)}</title><link href="${link}" rel="alternate"/><id>${link}</id><summary type="html">${xml(data.description)}</summary><author><name>${xml(data.feedAuthor)}</name></author><updated>${data.published.toISOString()}</updated></entry>`;
  }).join('');
  return kind === 'rss'
    ? `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>${xml(title)}</title><link>${feedUrl}</link><description>${description}</description>${items}</channel></rss>`
    : `<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>${xml(title)}</title><subtitle>${description}</subtitle><id>${feedUrl}</id><link href="${feedUrl}" rel="self"/><updated>${(posts[0]?.data.updated ?? new Date(0)).toISOString()}</updated>${items}</feed>`;
}
