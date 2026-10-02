import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';

const slug = z.string().regex(/^[A-Za-z0-9_-]+$/);
const posts = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/posts', generateId: ({ entry }) => entry }),
  schema: z.object({
    slug, title: z.string().min(1), category: slug, description: z.string(),
    draft: z.boolean().default(true), image: z.string().default('/media/default.webp'),
    imageAlt: z.string().default(''), imageAttribution: z.string().default(''),
    imageWidth: z.number().int().positive().nullable().default(null),
    imageHeight: z.number().int().positive().nullable().default(null),
    published: z.coerce.date(), updated: z.coerce.date(),
    author: z.string().default('John Solly'), feedAuthor: z.string().default('John_Solly'),
    excerpt: z.string().default(''),
    legacyId: z.number().int().optional(), related: z.array(slug).default([]),
  }),
});
const categories = defineCollection({
  loader: glob({ pattern: '*.json', base: './src/content/categories', generateId: ({ entry }) => entry }),
  schema: z.object({ slug, name: z.string().min(1), description: z.string(), legacyId: z.number().int().optional() }),
});
export const collections = { posts, categories };
