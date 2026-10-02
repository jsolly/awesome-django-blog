import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {recipeDocument,recipeBrief,recipeBundle} from './recipe-export.mjs';
const {recipes}=JSON.parse(readFileSync(new URL('./recipes.json',import.meta.url),'utf8'));
test('assistant/print document preserves safe pressure liquid, recalculated macros and separate chosen family servings',()=>{
 const r=recipes.find(r=>r.key==='salsa_chicken');
 const d=recipeDocument(r,{servings:2,units:'metric',familyDiners:1,familyChoice:{[r.id]:r.familyOptions[0].id}});
 assert.equal(d.ingredients.find(i=>/broth/i.test(i.name)).quantity,'375 ml');
 assert(Math.abs(d.nutrition.kcal-r.nutrition.kcal-6.5625)<1e-9);
 assert.equal(d.familyDiners,1);assert(d.familyIngredient);assert.equal(d.steps.length,r.steps.length);
 assert.match(recipeBrief(r,{servings:2,units:'metric'}),/74°C \(165°F\)/);
 assert(d.sources.every(s=>s.url.startsWith('https://')));
});
test('exports keep family choices, food states, allergies, limits and tiny spoon measures',()=>{
 const r=recipes.find(r=>r.key==='turkey');const o=r.familyOptions.find(o=>o.id==='pita_one');
 const d=recipeDocument(r,{servings:8,units:'metric',familyDiners:3,familyChoice:{[r.id]:o.id}});
 assert.equal(d.familyIngredient.choiceId,o.id);assert.equal(d.familyIngredient.quantity,'180 g');assert(d.allergens.includes('wheat'));
 assert(d.ingredients.every(i=>i.state));assert.match(d.capacity,/extra pan or basket batches/);assert.match(d.disclaimer,/not been cooked/);
 assert.doesNotMatch(d.ingredients.find(i=>i.name==='Olive oil').quantity,/ g$/);
 const noFamily=recipeDocument(r,{familyDiners:0});assert.equal(noFamily.familyIngredient,null);assert(!noFamily.allergens.includes('wheat'));
 const d2=recipeDocument(recipes.find(r=>r.key==='salmon'),{servings:2,units:'metric'});
 assert.equal(d2.ingredients.find(i=>i.name==='Lemon zest').quantity,'½ tsp');
 const bundle=JSON.parse(JSON.stringify(recipeBundle(recipes,{servings:4,units:'us',familyDiners:0})));
 assert.equal(bundle.recipes.length,12);assert.equal(new Set(bundle.recipes.map(r=>r.recipeId)).size,12);
 assert(bundle.recipes.every(r=>r.sources.length&&r.steps.length&&r.ingredients.length&&r.image));
});
