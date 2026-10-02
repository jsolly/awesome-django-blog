import assert from 'node:assert/strict';
import { readFile, writeFile, unlink, readdir, access } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';
import { serializePost } from './content-files.mjs';

const slug = `draft-contract-${randomUUID()}`;
const path = `src/content/posts/${slug}.md`;
const secret = 'draft-contract-private-sentinel-20261002';
const draft = {
  slug, title: secret, body: `<p>${secret}</p>`, description: secret,
  category: 'uncategorized', draft: true, published: '2026-10-02T00:00:00Z', updated: '2026-10-02T00:00:00Z',
};
await writeFile(path, serializePost(draft), { flag: 'wx' });
try {
  execFileSync('npm', ['run', 'build'], { stdio: 'pipe' });
  const scan = async directory => {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const file = join(directory, entry.name);
      if (entry.isDirectory()) await scan(file);
      else {
        const bytes = await readFile(file);
        for (const marker of [slug, secret]) assert.ok(!bytes.includes(Buffer.from(marker)), `Draft leaked into ${file}`);
      }
    }
  };
  await scan('dist');
  await assert.rejects(access(`dist/post/${slug}`), { code: 'ENOENT' }, 'Draft route must not exist');
  process.stdout.write('Verified a real draft is absent from every built asset.\n');
} finally {
  await unlink(path);
  // Restore the actual production candidate, even after a failed draft assertion.
  execFileSync('npm', ['run', 'build'], { stdio: 'pipe' });
}
