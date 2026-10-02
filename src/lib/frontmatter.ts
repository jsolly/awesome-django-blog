import { parseFrontmatter } from 'astro/markdown';
import { parseDocument } from 'yaml';

// PagesCMS writes YAML 1.2 strings, including unquoted ISO timestamps.
// Parse the raw values consistently before Astro's schema converts display dates.
export function parsePost(source: string): Record<string, unknown> & { body: string } {
  const { rawFrontmatter, content } = parseFrontmatter(source);
  const document = parseDocument(rawFrontmatter, { schema: 'core' });
  if (document.errors.length) throw document.errors[0];
  const metadata: unknown = document.toJS();
  if (!metadata || typeof metadata !== 'object' || Array.isArray(metadata)) throw new Error('Post frontmatter must be a YAML mapping');
  return { ...metadata, body: content.trim() };
}
