import assert from 'node:assert/strict';
import { readdir, readFile, writeFile, unlink } from 'node:fs/promises';
import { execFileSync, spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { join } from 'node:path';

const created = new Set();
try {
  for (const [collection, extension, label] of [['posts', 'md', 'post'], ['categories', 'json', 'category']]) {
    const directory = `src/content/${collection}`;
    const original = (await readdir(directory)).filter(file => file.endsWith(`.${extension}`)).sort()[0];
    assert.ok(original, `No ${collection} available for the collision contract`);
    const duplicate = join(directory, `identity-contract-${randomUUID()}.${extension}`);
    // An identical copy must fail too: Astro's default slug IDs can silently deduplicate it.
    await writeFile(duplicate, await readFile(join(directory, original)), { flag: 'wx' });
    created.add(duplicate);
    const build = spawnSync('npm', ['run', 'build'], { encoding: 'utf8' });
    assert.ifError(build.error);
    assert.notEqual(build.status, 0, `Duplicate ${label} identities must fail the build`);
    assert.match(build.stdout + build.stderr, new RegExp(`Duplicate ${label} slug:`));
    await unlink(duplicate);
    created.delete(duplicate);
  }
  process.stdout.write('Verified identical post and category slug collisions fail the build.\n');
} finally {
  for (const path of created) await unlink(path);
  execFileSync('npm', ['run', 'build'], { stdio: 'pipe' });
}
