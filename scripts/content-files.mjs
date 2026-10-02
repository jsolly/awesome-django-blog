import { parseFrontmatter } from 'astro/markdown';
import { stringify } from 'yaml';

export function parsePost(source) {
  const { frontmatter, content } = parseFrontmatter(source);
  return { ...frontmatter, body: content.trim() };
}

export function serializePost(post) {
  const { body, ...metadata } = post;
  return `---\n${stringify(metadata, { lineWidth: 0, compat: 'yaml-1.1' })}---\n\n${body.trim()}\n`;
}
