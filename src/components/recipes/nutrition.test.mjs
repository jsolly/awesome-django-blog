import {test} from 'node:test';
import assert from 'node:assert/strict';
import recipes from './recipes.json' with {type:'json'};
import data from './nutrition-data.json' with {type:'json'};
import {dailyNutrition,nutrientAmount} from './nutrition.mjs';
import {ingredientAmount} from './recipe-logic.mjs';
test('Daily Values use edible weights, include salt, and scale minimum broth per serving',()=>{
 const chicken=recipes.recipes.find(r=>r.key==='smoky_chicken');
 const sodium=dailyNutrition(chicken,4,ingredientAmount).find(n=>n.key==='sodium');
 const salt=data.recipes[chicken.id].find(r=>r.food==='salt');
 assert.ok(sodium.amount>=salt.nutrients.sodium*salt.grams/400);
 assert.equal(sodium.percent,Math.round(sodium.amount/2300*100));
 const b12=dailyNutrition(chicken,4,ingredientAmount).find(n=>n.key==='vitamin_b12');assert.ok(b12.amount>=9/4);
 const salsa=recipes.recipes.find(r=>r.key==='salsa_chicken');
 assert.ok(dailyNutrition(salsa,2,ingredientAmount).find(n=>n.key==='sodium').amount>dailyNutrition(salsa,4,ingredientAmount).find(n=>n.key==='sodium').amount);
 for(const recipe of recipes.recipes){const base=dailyNutrition(recipe,4,ingredientAmount);for(const n of [2,6,8]){const values=dailyNutrition(recipe,n,ingredientAmount);for(let i=0;i<base.length;i++){if(base[i].amount===null){assert.equal(values[i].amount,null);continue;}assert(Number.isFinite(values[i].amount));if(recipe.key!=='salsa_chicken')assert.ok(Math.abs(values[i].amount-base[i].amount)<1e-8);}}}
});
test('small nutrient amounts stay visible and missing observations stay missing',()=>{assert.equal(nutrientAmount(.03),'<0.1');assert.equal(nutrientAmount(null),'—');assert.equal(nutrientAmount(0),'0');});

test('missing ingredient observations cannot become partial daily totals',()=>{const recipe=recipes.recipes.find(r=>r.key==='smoky_chicken');assert.equal(dailyNutrition(recipe,4,ingredientAmount).find(n=>n.key==='pantothenic_acid').amount,null);});
