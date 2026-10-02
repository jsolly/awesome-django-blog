import test from 'node:test';
import assert from 'node:assert/strict';
import { canonicalHash, recipeSlug, verifyRecipeRewrite } from './migration-rewrites.mjs';

test('rewrite pins source and replacement while preserving editorial identity', () => {
  const record = { model: 'blog.post', pk: 116, fields: { slug: recipeSlug, title: 'Original', content: 'Original body' } };
  const imported = { slug: recipeSlug, title: 'Original', body: 'Original body', published: '2023-01-10', category: 'resources', draft: false, related: ['first', 'second'], legacyId: 116 };
  const replacement = { ...imported, title: 'New guide', body: 'Reviewed complete recipes' };
  const receipt = { slug: recipeSlug, sourceRecordSha256: canonicalHash(record), replacementPostSha256: canonicalHash(replacement) };
  verifyRecipeRewrite(receipt, record, imported, replacement);
  assert.equal(canonicalHash({ a: 1, b: 2 }), canonicalHash({ b: 2, a: 1 }));
  assert.throws(() => verifyRecipeRewrite(receipt, { ...record, fields: { ...record.fields, content: 'New legacy-source edit' } }, imported, replacement), /source changed/u);
  assert.throws(() => verifyRecipeRewrite(receipt, record, imported, { ...replacement, body: 'Unreviewed replacement' }), /replacement changed/u);
  for (const [field, value] of Object.entries({ slug: 'different-url', published: '2026-10-02', category: 'other', draft: true, related: ['second', 'first'], legacyId: 99 })) {
    const changed = { ...replacement, [field]: value };
    const changedReceipt = { ...receipt, replacementPostSha256: canonicalHash(changed) };
    assert.throws(() => verifyRecipeRewrite(changedReceipt, record, imported, changed), /must preserve/u);
  }
});
