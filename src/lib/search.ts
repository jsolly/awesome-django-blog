import MiniSearch from 'minisearch';
import { z } from 'zod';

export const searchEntry = z.object({ slug: z.string(), title: z.string(), description: z.string(), text: z.string() });
export type SearchEntry = z.infer<typeof searchEntry>;

export function createArticleSearch(entries: SearchEntry[]) {
  const documents = new Map(entries.map(entry => [entry.slug, entry]));
  const index = new MiniSearch<SearchEntry>({
    idField: 'slug',
    fields: ['title', 'description', 'text'],
    searchOptions: {
      boost: { title: 8, description: 3, text: 1 },
      combineWith: 'AND',
      prefix: term => term.length >= 2,
      fuzzy: term => term.length >= 5 ? 0.25 : term.length === 4 ? 0.2 : false,
      maxFuzzy: 2,
    },
  });
  index.addAll(entries);
  return (query: string): SearchEntry[] => {
    if (!query.trim()) return [];
    return index.search(query).flatMap(result => {
      const entry = documents.get(result.id);
      return entry ? [entry] : [];
    });
  };
}
