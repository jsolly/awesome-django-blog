import assert from 'node:assert/strict';
import { readFile, writeFile, unlink } from 'node:fs/promises';
import { execFileSync, spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { load } from 'cheerio';

const slug = `cms-contract-${randomUUID()}`;
const path = `src/content/posts/${slug}.md`;
// Match hosted PagesCMS serialization: unquoted dates and absent empty optional fields.
const source = `---
slug: ${slug}
title: CMS source compatibility
category: uncategorized
description: Test the actual authoring format.
draft: false
published: 2026-10-02T14:00:23.123456-04:00
updated: 2026-10-02T14:00:23.123456-04:00
---
<p>Retain this source.</p>

<pre><code>  keep indentation\n</code></pre>
`;
await writeFile(path, source, { flag: 'wx' });
try {
  execFileSync('npm', ['run', 'build'], { stdio: 'pipe' });
  const $ = load(await readFile(`dist/post/${slug}/index.html`, 'utf8'));
  assert.equal($('h1').clone().find('.heading-link').remove().end().text(), 'CMS source compatibility');
  assert.equal($('.article-body pre code').text(), '  keep indentation\n');
  assert.equal($('time').first().attr('datetime'), '2026-10-02T18:00:23.123Z');
  assert.equal(JSON.parse($('script[type="application/ld+json"]').text()).author.name, 'John Solly', 'Missing optional author must use its public metadata default');
  for (const invalid of ['2026-10-02', '2026-10-02T14:00:23']) {
    await writeFile(path, source.replace('published: 2026-10-02T14:00:23.123456-04:00', `published: ${invalid}`));
    const build = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.ifError(build.error);
    assert.notEqual(build.status, 0, 'A date without time and timezone must fail validation');
    assert.match(build.stdout + build.stderr, /published/u);
  }
  process.stdout.write('Verified CMS YAML builds with source precision intact; incomplete timestamps fail.\n');
} finally {
  await unlink(path);
  execFileSync('npm', ['run', 'build'], { stdio: 'pipe' });
}
