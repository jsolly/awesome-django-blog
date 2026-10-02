import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { glob } from 'astro/loaders';
import { postLoader } from './lib/post-loader';

const slug = z.string().regex(/^[A-Za-z0-9_-]+$/);
const timestamp = z.iso.datetime({ offset: true }).pipe(z.coerce.date());
const posts = defineCollection({
  loader: postLoader(),
  schema: z.object({
    slug, title: z.string().min(1), category: slug, description: z.string(),
    draft: z.boolean().default(true), image: z.string().default('/media/default.webp'),
    imageAlt: z.string().default(''), imageAttribution: z.string().default(''),
    imageWidth: z.number().int().positive().nullable().default(null),
    imageHeight: z.number().int().positive().nullable().default(null),
    published: timestamp, updated: timestamp,
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
