import test from 'node:test';
import assert from 'node:assert/strict';
import { createArticleSearch } from '../src/lib/search.ts';

const entries = [
  { slug: 'recipes', title: 'Instant Pot recipes', description: 'Fast weeknight meals', text: 'Chicken vegetables pressure cooking' },
  { slug: 'rules', title: 'Solly Agent Rules', description: 'Global coding instructions', text: 'Agents must review code' },
  { slug: 'mention', title: 'Software tools', description: 'Programming tools', text: 'This article mentions instant pot recipes while discussing software.' },
];
const search = createArticleSearch(entries);

test('A title match ranks above an incidental body mention', () => {
  assert.equal(search('instant pot')[0]?.slug, 'recipes');
});
test('A reader finds a title despite a transposed letter or unfinished words', () => {
  assert.equal(search('recipse')[0]?.slug, 'recipes');
  assert.equal(search('agen rul')[0]?.slug, 'rules');
});
test('Unrelated and empty queries do not return arbitrary articles', () => {
  assert.deepEqual(search('zzzznomatch'), []);
  assert.deepEqual(search('   '), []);
  assert.deepEqual(search('instant rules'), []);
});
