import { stringify } from 'yaml';

export function serializePost(post) {
  const { body, ...metadata } = post;
  return `---\n${stringify(metadata, { lineWidth: 0, compat: 'yaml-1.1' })}---\n\n${body.trim()}\n`;
}
