import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {generateRecipeArticle} from './article-generator.mjs';

const source=readFileSync(new URL('../../src/content/posts/15-minute-dump-and-go-instant-pot-recipes.md',import.meta.url),'utf8');
const data=JSON.parse(readFileSync(new URL('../../src/components/recipes/recipes.json',import.meta.url),'utf8'));
const region=(article,key)=>article.slice(article.indexOf(`<!-- recipe-generated:${key}:begin -->`),article.indexOf(`<!-- recipe-generated:${key}:end -->`)+`<!-- recipe-generated:${key}:end -->`.length);

test('canonical title changes regenerate the same stable recipe region and anchor',()=>{
 const changed=structuredClone(data);
 changed.recipes[0].title='Lemon salmon: a revised title';
 const generated=generateRecipeArticle(source,changed);
 const owned=region(generated,`recipe:${changed.recipes[0].id}`);
 assert.ok(owned.includes(`### ${changed.recipes[0].title}`));
 assert.ok(owned.includes(`<div id="${data.recipes[0].id}"></div>`));
 assert.ok(region(generated,'table:overview').includes(changed.recipes[0].title));
 assert.equal(generateRecipeArticle(generated,changed),generated);
});

test('editorial HTML tables and prose outside generated regions remain byte-identical',()=>{
 const editorial='\n## My cooking notes\n\n<table><tr><td>Keep this editorial table.</td></tr></table>\n';
 const generated=generateRecipeArticle(source+editorial,data);
 assert.ok(generated.endsWith(editorial));
 assert.ok(generated.includes("## Read this once before cooking\n"));
 assert.equal(generateRecipeArticle(generated,data),generated);
});

test('comparison table ownership follows its key after editorial reordering',()=>{
 const overview=region(source,'table:overview');
 const family=region(source,'table:family');
 const reordered=source.replace(overview,'OVERVIEW_PLACEHOLDER').replace(family,overview).replace('OVERVIEW_PLACEHOLDER',family);
 const generated=generateRecipeArticle(reordered,data);
 assert.ok(generated.indexOf('table:family:begin')<generated.indexOf('table:overview:begin'));
 assert.match(region(generated,'table:family'),/<th scope="col">One family add-on per person<\/th>/u);
 assert.match(region(generated,'table:overview'),/<th scope="col">Attention and finish checks<\/th>/u);
 assert.equal(generateRecipeArticle(generated,data),generated);
});

test('missing, duplicate and inverted boundaries fail without returning partially generated content',()=>{
 const begin='<!-- recipe-generated:table:overview:begin -->';
 const end='<!-- recipe-generated:table:overview:end -->';
 for(const malformed of [source.replace(begin,''),source.replace(begin,begin+begin),source.replace(begin,'END_PLACEHOLDER').replace(end,begin).replace('END_PLACEHOLDER',end)]) {
  assert.throws(()=>generateRecipeArticle(malformed,data),/Missing, duplicate or inverted generated region: table:overview/u);
 }
});

test('nested and crossing editor markers reject regeneration before a recipe can be removed',()=>{
 const first=`<!-- recipe-generated:recipe:${data.recipes[0].id}:begin -->`;
 const second=`<!-- recipe-generated:recipe:${data.recipes[1].id}:begin -->`;
 const secondEnd=`<!-- recipe-generated:recipe:${data.recipes[1].id}:end -->`;
 const nested=source.replace(second,'').replace(first,second+'\n'+first);
 const crossing=nested.replace(secondEnd,'').replace(first,first+'\n'+secondEnd);
 for(const malformed of [crossing,nested]) assert.throws(()=>generateRecipeArticle(malformed,data),/Overlapping generated regions/u);
});
