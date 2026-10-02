import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

export const recipeSlug = '15-minute-dump-and-go-instant-pot-recipes';
export const recipeRewriteFields = [
  'title', 'description', 'image', 'imageAlt', 'imageAttribution',
  'imageWidth', 'imageHeight', 'updated', 'excerpt', 'body',
];

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  }
  return value;
}

export function canonicalHash(value) {
  return createHash('sha256').update(JSON.stringify(canonical(value))).digest('hex');
}

export function verifyRecipeRewrite(receipt, sourceRecord, importedPost, replacementPost) {
  assert.equal(receipt.slug, recipeSlug, 'Only the authorized recipe article may be rewritten');
  assert.equal(sourceRecord.fields.slug, receipt.slug);
  assert.equal(canonicalHash(sourceRecord), receipt.sourceRecordSha256, 'Recipe source changed after the authorized rewrite; reconcile the final export');
  assert.equal(canonicalHash(replacementPost), receipt.replacementPostSha256, 'Recipe replacement changed after review; renew its rewrite receipt');
  for (const [field, expected] of Object.entries(importedPost)) {
    if (!recipeRewriteFields.includes(field)) assert.deepEqual(replacementPost[field], expected, `Recipe rewrite must preserve ${field}`);
  }
}
