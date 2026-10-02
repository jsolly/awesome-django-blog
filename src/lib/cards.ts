import type { Post, Category } from './content';
import { dateLabel } from './content';
import { imageUrl, plainText, articleHtml } from './html';
import type { Card } from '../components/PostCards.svelte';

export function cards(posts: Post[], categories: Category[]): Card[] {
  return posts.map(({ data, html }) => ({
    slug: data.slug, title: data.title, description: data.description,
    excerpt: articleHtml(data.excerpt),
    image: imageUrl(data.image), imageAlt: data.imageAlt,
    imageWidth: data.imageWidth, imageHeight: data.imageHeight,
    published: data.published.toISOString(), updated: data.updated.toISOString(),
    dateLabel: dateLabel(data.published), updatedLabel: dateLabel(data.updated),
    category: data.category, categoryName: categories.find(category => category.data.slug === data.category)?.data.name ?? data.category,
    minutes: Math.max(1, Math.ceil(plainText(html).split(/\s+/u).length / 238)),
  }));
}
