import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {readFile} from 'node:fs/promises';
import {
  capacityNote, familyNutrition, filterRecipes, formatIngredient, formatQuantity,
  ingredientAmount, shoppingList, temperature, validateSettings, servingNutrition,
} from './recipe-logic.mjs';

const ingredient = (id, name, amount, unit, state = 'raw', extra = {}) => ({
  id, name, amount, unit, state, category: 'produce', scale: 'linear', ...extra,
});
const nutrition = { kcal: 400, protein_g: 35, carbs_g: 12, fiber_g: 3, net_carbs_g: 9 };
const chicken = {
  id: 'chicken', key: 'salsa_chicken', title: 'Salsa chicken', group: 'shared',
  proteinType: 'chicken', vegetarian: false, appliance: 'instant-pot',
  activeMinutes: 15, totalMax: 45, timeVariable: true,
  allergens: [], boosters: ['hemp hearts'],
  ingredients: [
    ingredient('chicken-breast', 'chicken breast', 800, 'g', 'raw', {
      category: 'meat', us: { amount: 1.75, unit: 'lb' },
    }),
    ingredient('lime', 'lime juice', 30, 'ml', 'juiced', {
      us: { amount: 2, unit: 'tbsp' },
    }),
    ingredient('salt', 'salt', 1, 'tsp', 'dry', {
      category: 'pantry', scale: 'minimum', us: { amount: 1, unit: 'tsp' },
    }),
  ],
  familyOptions: [{
    id: 'rice', label: 'Brown rice', ingredientId: 'rice', ingredientName: 'cooked brown rice',
    amount: 150, unit: 'g', state: 'cooked', category: 'grains',
    nutrition: { kcal: 166, protein_g: 4, carbs_g: 34, fiber_g: 2, net_carbs_g: 32 },
  }], nutrition,
};
const fish = {
  id: 'fish', key: 'salmon', title: 'Herbed salmon', group: 'keto',
  proteinType: 'fish', vegetarian: false, appliance: 'air-fryer',
  activeMinutes: 8, totalMax: 25, timeVariable: false,
  allergens: ['fish'], boosters: [],
  ingredients: [
    ingredient('lime', 'lime juice', 15, 'ml', 'juiced', { us: { amount: 1, unit: 'tbsp' } }),
    ingredient('broccoli', 'broccoli', 500, 'g', 'raw', { us: { amount: 1.1, unit: 'lb' } }),
  ], nutrition: { ...nutrition, protein_g: 42 },
};
const bake = {
  id: 'bake', key: 'lentil_bake', title: 'Lentil bake', group: 'nonketo',
  proteinType: 'plant-forward', vegetarian: true, appliance: 'oven',
  activeMinutes: 10, totalMax: 40, timeVariable: false,
  allergens: ['milk'], boosters: [],
  ingredients: [ingredient('lentils', 'cooked lentils', 400, 'g', 'cooked')],
  nutrition: { ...nutrition, protein_g: 25 },
};

test('scaled ounce rounding agrees between recipe and consolidated groceries', () => {
  const { recipes } = JSON.parse(readFileSync(new URL('./recipes.json', import.meta.url), 'utf8'));
  for (const recipe of recipes) {
    const groceries = shoppingList([recipe], [recipe.id], { servings: 6, familyDiners: 0 });
    for (const ingredient of recipe.ingredients.filter(item => item.us?.unit === 'oz')) {
      const grocery = groceries.find(item => item.id === ingredient.id && item.state === ingredient.state && item.unit === ingredient.unit);
      assert.equal(formatIngredient(ingredient, 6, 'us'), formatIngredient({ ...grocery, scale: 'fixed' }, 4, 'us'), `${recipe.id}: ${ingredient.name}`);
      if (ingredient.us.amount === 16.9) assert.equal(formatIngredient(ingredient, 6, 'us'), '25.4 oz');
    }
  }
});

test('familiar fractions, typed US measures, and seasoning rules survive serving changes', () => {
  assert.equal(formatQuantity(1.5), '1 ½');
  assert.equal(formatQuantity(0.3333), '⅓');
  assert.equal(formatQuantity(37.5), '37.5');
  assert.equal(formatIngredient(chicken.ingredients[1], 2, 'us'), '1 tbsp');
  assert.equal(formatIngredient(chicken.ingredients[1], 2, 'metric'), '15 ml');
  assert.equal(formatIngredient(chicken.ingredients[0], 8, 'us'), '3 ½ lb');
  assert.equal(ingredientAmount(chicken.ingredients[2], 2), 1);
  assert.equal(formatIngredient(chicken.ingredients[2], 2, 'us'), '1 tsp');
  assert.equal(ingredientAmount(chicken.ingredients[2], 8), 2);
  const fixedEgg = ingredient('egg', 'beaten egg', 1, 'count', 'beaten', { scale: 'fixed' });
  assert.equal(ingredientAmount(fixedEgg, 8), 1);
  const linearEgg = { ...fixedEgg, scale: 'linear' };
  assert.equal(formatIngredient(linearEgg, 2), '½ count');
  assert.equal(formatIngredient(ingredient('pepper', 'black pepper', 0, 'tsp'), 8), 'to taste');
});

test('temperature keeps the source setting and rounds safe endpoints upward', () => {
  assert.equal(temperature(425, 'metric'), '220°C (425°F)');
  assert.equal(temperature(165, 'metric', true), '74°C (165°F)');
  assert.equal(temperature(145, 'metric', true), '63°C (145°F)');
  assert.equal(temperature(165, 'us', true), '165°F');
});

test('filters are conjunctive, search ingredients, and reject variable deadlines', () => {
  const recipes = [chicken, fish, bake];
  assert.deepEqual(filterRecipes(recipes, { query: 'lime', group: 'keto' }).map((r) => r.id), ['fish']);
  assert.deepEqual(filterRecipes(recipes, {
    query: 'lime', group: 'shared', appliance: 'instant-pot',
    maxActive: 15, proteinType: 'chicken', booster: 'hemp hearts',
  }).map((r) => r.id), ['chicken']);
  assert.deepEqual(filterRecipes(recipes, { maxTotal: 45 }).map((r) => r.id), ['fish', 'bake']);
  assert.deepEqual(filterRecipes(recipes, { proteinType: 'vegetarian' }).map((r) => r.id), ['bake']);
  assert.deepEqual(filterRecipes(recipes, { avoidAllergens: ['fish', 'milk'] }).map((r) => r.id), ['chicken']);
  assert.deepEqual(filterRecipes(recipes, { query: 'no such ingredient' }), []);
  assert.deepEqual(filterRecipes(recipes, { sort: 'protein' }).map((r) => r.id), ['fish', 'chicken', 'bake']);
  assert.deepEqual(filterRecipes([{ ...fish, totalMax: undefined }], { maxTotal: 30 }), []);
});

test('shopping list combines compatible states and adds starch only for chosen family diners', () => {
  const list = shoppingList([chicken, fish], ['chicken', 'fish', 'chicken'], {
    servings: 8, familyDiners: 3, familyChoice: { chicken: 'rice' },
  });
  assert.equal(list.find((line) => line.id === 'lime').amount, 90);
  assert.deepEqual(list.find((line) => line.id === 'lime').us, { amount: 6, unit: 'tbsp' });
  assert.equal(list.find((line) => line.id === 'salt').amount, 2);
  assert.equal(list.find((line) => line.id === 'rice').amount, 450);
  assert.equal(list.find((line) => line.id === 'rice').state, 'cooked');
  assert.equal(shoppingList([chicken], ['chicken'], { servings: 4, familyDiners: 3 })
    .find((line) => line.id === 'rice').amount, 450);
  assert.equal(shoppingList([chicken], ['chicken'], { servings: 4, familyDiners: 3,
    familyChoice: { chicken: 'invalid' } }).find((line) => line.id === 'rice').amount, 450);
  const distinct = shoppingList([
    { ...fish, id: 'raw', ingredients: [ingredient('tomato', 'tomato', 200, 'g', 'raw')] },
    { ...fish, id: 'cooked', ingredients: [ingredient('tomato', 'tomato', 100, 'g', 'cooked')] },
  ], ['raw', 'cooked'], { servings: 4 });
  assert.equal(distinct.filter((line) => line.id === 'tomato').length, 2);
  const mixedConversions = shoppingList([
    { ...fish, id: 'a', ingredients: [ingredient('sauce', 'sauce', 100, 'ml', 'bottled', { us: { amount: 7, unit: 'tbsp' } })] },
    { ...fish, id: 'b', ingredients: [ingredient('sauce', 'sauce', 100, 'ml', 'bottled', { us: { amount: 6, unit: 'tbsp' } })] },
  ], ['a', 'b'], { servings: 4 });
  assert.equal(mixedConversions[0].amount, 200);
  assert.equal(mixedConversions[0].us, undefined);
});

test('family macros are per serving and base remains intact', () => {
  assert.deepEqual(familyNutrition(chicken, 'rice'), {
    kcal: 566, protein_g: 39, carbs_g: 46, fiber_g: 5, net_carbs_g: 41,
  });
  assert.deepEqual(familyNutrition(chicken, 'unknown'), familyNutrition(chicken,'rice')); 
  assert.deepEqual(chicken.nutrition, nutrition);
});

test('invalid settings fail to a safe four-serving plan and capacity messaging is honest', () => {
  assert.deepEqual(validateSettings({ servings: 5, familyDiners: -1, units: 'cups' }), {
    servings: 4, familyDiners: 0, units: 'us',
  });
  assert.deepEqual(validateSettings({ servings: 6, familyDiners: 20, units: 'metric' }), {
    servings: 6, familyDiners: 6, units: 'metric',
  });
  assert.match(capacityNote(8), /extra pan or basket batches/);
  assert.match(capacityNote(2), /do not shorten a pressure minimum/);
});

test('the 12 published recipes keep to-taste pantry items in a real shopping plan', () => {
  const data = JSON.parse(readFileSync(new URL('./recipes.json', import.meta.url), 'utf8'));
  assert.equal(data.recipes.length, 12);
  const list = shoppingList(data.recipes, data.recipes.map((recipe) => recipe.id), {
    servings: 4, familyDiners: 0,
  });
  const pepper = list.find((item) => item.id === 'black_pepper' && item.state === 'dry');
  assert.ok(pepper);
  assert.equal(pepper.amount, 0);
  assert.equal(pepper.category, 'pantry');
  assert.ok(list.some((item) => item.id === 'hemp_hearts'));
});

test('published default family choices and explicit bread choices total in metric and US units', () => {
  const { recipes } = JSON.parse(readFileSync(new URL('./recipes.json', import.meta.url), 'utf8'));
  const shawarma = recipes.find((recipe) => recipe.key === 'shawarma');
  const salsa = recipes.find((recipe) => recipe.key === 'salsa_chicken');
  const turkey = recipes.find((recipe) => recipe.key === 'turkey');
  const defaults = shoppingList(recipes, [shawarma.id, salsa.id], {
    servings: 4, familyDiners: 2, familyChoice: { [shawarma.id]: 'invalid' },
  });
  const rice = defaults.find((line) => line.id === 'cooked_rice');
  assert.equal(rice.amount, 320);
  assert.equal(rice.state, 'fully cooked, ready to heat');
  assert.deepEqual(rice.us, { amount: 2, unit: 'cup' });

  const bread = shoppingList(recipes, [shawarma.id, turkey.id], {
    servings: 4, familyDiners: 2,
    familyChoice: { [shawarma.id]: 'pita_one', [turkey.id]: 'pita_one' },
  }).find((line) => line.id === 'pita');
  assert.equal(bread.amount, 240);
  assert.deepEqual(bread.us, { amount: 4, unit: 'count' });
});

test('real booster IDs, served family allergen exclusions, and state-keyed lines reconcile', async()=>{
 const data=JSON.parse(await readFile(new URL('./recipes.json',import.meta.url),'utf8')).recipes;
 assert.equal(filterRecipes(data,{booster:'flax'}).length,1);
 assert.equal(filterRecipes(data,{booster:'yeast'}).length,4);
 const turkey=data.find(r=>r.key==='turkey');
 assert(!filterRecipes(data,{avoidAllergens:['wheat'],familyDiners:2}).some(r=>r.id===turkey.id));
 assert(filterRecipes(data,{avoidAllergens:['wheat'],familyDiners:0}).some(r=>r.id===turkey.id));
 const list=shoppingList(data,data.filter(r=>['smoky_chicken','shawarma'].includes(r.key)).map(r=>r.id),{servings:4,familyDiners:0});
 const chicken=list.filter(i=>i.id==='chicken_thigh');assert.equal(chicken.length,2);
 assert.notEqual(JSON.stringify([chicken[0].id,chicken[0].state,chicken[0].unit]),JSON.stringify([chicken[1].id,chicken[1].state,chicken[1].unit]));
});

test('US consolidation uses typed weight or volume fallback and practical precision',async()=>{
 const data=JSON.parse(await readFile(new URL('./recipes.json',import.meta.url),'utf8')).recipes;
 const list=shoppingList(data,data.map(r=>r.id),{servings:4,familyDiners:2});
 for(const item of list){if(item.unit==='g'&&!item.us)assert.match(formatIngredient({...item,scale:'fixed'},4,'us'),/ oz$/);if(item.unit==='ml'&&!item.us)assert.match(formatIngredient({...item,scale:'fixed'},4,'us'),/ fl oz$/);}
 const salmon=data.find(r=>r.key==='salmon').ingredients[0];assert.equal(formatIngredient(salmon,4,'us'),'1 ½ lb');assert.equal(formatIngredient(salmon,8,'us'),'3 lb');
});


test('pressure minimum changes small-batch per-person nutrition, not safe liquid',async()=>{
 const data=JSON.parse(await readFile(new URL('./recipes.json',import.meta.url),'utf8')).recipes;
 const pressure=data.find(r=>r.key==='salsa_chicken');const p=servingNutrition(pressure,2);
 assert(Math.abs(p.kcal-pressure.nutrition.kcal-6.5625)<1e-10);
 assert(Math.abs(p.protein_g-pressure.nutrition.protein_g-1.275)<1e-10);
 assert(Math.abs(p.carbs_g-pressure.nutrition.carbs_g-.35625)<1e-10);
 assert.deepEqual(servingNutrition(pressure,4),pressure.nutrition);
 assert.deepEqual(servingNutrition(pressure,8),pressure.nutrition);
 assert.deepEqual(familyNutrition(pressure,'bogus',2),familyNutrition(pressure,pressure.familyOptions[0].id,2));
});

test('package counts follow scaled and consolidated weights rather than fixed recipe notes',async()=>{
 const {purchaseNote}=await import('./recipe-logic.mjs');
 const data=JSON.parse(await readFile(new URL('./recipes.json',import.meta.url),'utf8')).recipes;
 const chickpea=data.find(r=>r.key==='chickpea').ingredients.find(i=>i.id==='chickpeas_canned');
 assert.match(purchaseNote(chickpea,2),/About 1 ×/);assert.match(purchaseNote(chickpea,8),/About 4 ×/);
 const spinach=data.find(r=>r.key==='frittata').ingredients.find(i=>i.id==='spinach_frozen');assert.match(purchaseNote(spinach,8),/Buy 2 ×/);
 const rows=shoppingList(data,data.map(r=>r.id),{servings:8,familyDiners:0});const gnocchi=rows.find(i=>i.id==='shelf_stable_gnocchi');assert.match(purchaseNote({...gnocchi,scale:'fixed'},4),/Buy 2 ×/);
});

test('small finishing amounts use spoons in both modes without changing nutrition weights', async()=>{
 const data=JSON.parse(await readFile(new URL('./recipes.json',import.meta.url),'utf8')).recipes;
 for(const r of data)for(const i of r.ingredients.filter(i=>i.displayMeasure==='spoon')){
  for(const count of [2,4,6,8]){assert.equal(formatIngredient(i,count,'metric'),formatIngredient(i,count,'us'));assert.doesNotMatch(formatIngredient(i,count,'metric'),/ g$/);}
 }
 const salmon=data.find(r=>r.key==='salmon');const zest=salmon.ingredients.find(i=>i.id==='lemon_zest');
 assert.equal(zest.amount,2);assert.equal(formatIngredient(zest,2,'metric'),'½ tsp');
 const list=shoppingList(data,[salmon.id],{servings:2});assert.equal(formatIngredient({...list.find(i=>i.id==='lemon_zest'),scale:'fixed'},4,'metric'),'½ tsp');
});
