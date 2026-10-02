import { readFile } from 'node:fs/promises';
import { glob, type Loader } from 'astro/loaders';
import { parsePost } from './frontmatter';

export function postLoader(): Loader {
  const files = glob({ pattern: '*.md', base: './src/content/posts', generateId: ({ entry }) => entry });
  return {
    name: 'yaml-frontmatter-posts',
    async load(context) {
      await files.load({
        ...context,
        async parseData(entry) {
          if (!entry.filePath) throw new Error('Post loader requires a source file path');
          const { body: _body, ...data } = parsePost(await readFile(entry.filePath, 'utf8'));
          // Astro's generic denotes schema output; assert it only after framework validation.
          return context.parseData({ ...entry, data }) as Promise<typeof entry.data>;
        },
      });
    },
  };
}
