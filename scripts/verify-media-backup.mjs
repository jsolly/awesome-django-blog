import assert from 'node:assert/strict';
import { readFile, stat, writeFile } from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

export async function verifyMediaBackup(inventory, directory) {
  assert.ok(Array.isArray(inventory.Contents) && inventory.Contents.length, 'Empty or invalid S3 inventory');
  const root = resolve(directory);
  const objects = [];
  for (const object of inventory.Contents) {
    assert.ok(typeof object.Key === 'string' && !object.Key.includes('\\'), 'Invalid object key');
    const path = resolve(root, object.Key);
    assert.ok(path.startsWith(`${root}${sep}`), `Object escapes backup directory: ${object.Key}`);
    // S3 folder markers have no file payload; the inventory still records them.
    if (object.Key.endsWith('/') && object.Size === 0) continue;
    assert.ok(Number.isSafeInteger(object.Size) && object.Size >= 0, 'Invalid object size');
    const file = await stat(path);
    assert.ok(file.isFile() && file.size === object.Size, `Missing or truncated backup: ${object.Key}`);
    const hash = createHash('sha256');
    for await (const chunk of createReadStream(path)) hash.update(chunk);
    objects.push({ key: object.Key, bytes: file.size, etag: object.ETag, sha256: hash.digest('hex') });
  }
  return { objects, files: objects.length, bytes: objects.reduce((sum, object) => sum + object.bytes, 0) };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const [, , inventoryPath, directory, receiptPath] = process.argv;
  if (!receiptPath) throw new Error('Usage: node scripts/verify-media-backup.mjs <inventory.json> <download-directory> <new-receipt.json>');
  const raw = await readFile(inventoryPath, 'utf8');
  const receipt = await verifyMediaBackup(JSON.parse(raw), directory);
  await writeFile(receiptPath, `${JSON.stringify({ bucket: 'blogthedata', inventorySha256: createHash('sha256').update(raw).digest('hex'), ...receipt }, null, 2)}\n`, { flag: 'wx' });
  process.stdout.write(`Verified ${receipt.files} files, ${receipt.bytes} bytes; SHA-256 receipt saved.\n`);
}
