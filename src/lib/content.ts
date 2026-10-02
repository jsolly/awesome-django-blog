import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'posts'> & { html: string };
export type Category = CollectionEntry<'categories'>;
export const site = 'https://www.blogthedata.com';

export async function blogContent() {
  const [entries, categories] = await Promise.all([getCollection('posts'), getCollection('categories')]);
  const posts: Post[] = entries.map(post => {
    if (!post.body?.trim() || !post.rendered?.html) throw new Error(`Empty article: ${post.data.slug}`);
    return { ...post, html: post.rendered.html };
  });
  const knownCategories = new Set<string>();
  for (const category of categories) {
    if (knownCategories.has(category.data.slug)) throw new Error(`Duplicate category slug: ${category.data.slug}`);
    knownCategories.add(category.data.slug);
  }
  const slugs = new Set<string>();
  for (const post of posts) {
    if (slugs.has(post.data.slug)) throw new Error(`Duplicate post slug: ${post.data.slug}`);
    if (!knownCategories.has(post.data.category)) throw new Error(`Unknown category: ${post.data.category}`);
    slugs.add(post.data.slug);
  }
  return {
    posts: posts.filter(post => !post.data.draft).sort((a, b) => b.data.published.getTime() - a.data.published.getTime()),
    categories: categories.sort((a, b) => a.data.name.localeCompare(b.data.name)),
  };
}

export function dateLabel(date: Date) {
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });
}
