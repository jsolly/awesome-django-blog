import {dailyNutrition} from './nutrition.mjs';
import {ingredientAmount} from './recipe-logic.mjs';
const immuneNutrients = new Set(['vitamin_a','vitamin_c','vitamin_d','zinc','selenium']);
export function nutrientFilters(recipe,servings){
 const nutrients=dailyNutrition(recipe,servings,ingredientAmount);
 const rich=n=>n.amount!==null && n.amount/n.dailyValue>=0.2;
 return {
  immune: nutrients.filter(n=>immuneNutrients.has(n.key)&&rich(n)).length>=2,
  iron: nutrients.some(n=>n.key==='iron'&&rich(n)),
 };
}

// Main starches and available family sides; vegetable carbs are not starch categories.
export const starchTypes={all:'All starches',rice:'Rice',pasta:'Pasta',bread:'Bread',tortillas:'Tortillas',potatoes:'Potatoes',legumes:'Legumes',none:'No starch',fruit:'Fruit'};
export const recipeStarches={
 'lemon-salmon-and-asparagus':['none'],
 'smoky-chicken-thighs-and-broccoli':['none'],
 'pesto-cod-and-zucchini':['none'],
 'spinach-feta-and-hemp-frittata':['none'],
 'shawarma-chicken-bowls':['rice','bread'],
 'sheet-pan-chicken-fajitas':['tortillas'],
 'salsa-verde-shredded-chicken':['rice'],
 'greek-turkey-patties':['bread'],
 'pan-fried-greek-turkey-patties':['bread'],
 'avocado-lime-smoothie':['none'],
 'strawberry-avocado-smoothie':['fruit'],
 'strawberry-banana-smoothie':['fruit'],
 'banana-flax-smoothie':['fruit'],
 'tomato-lentil-and-chicken-bake':['legumes'],
 'harissa-chickpea-and-cauliflower-bowls':['legumes'],
 'lemon-chicken-potatoes-and-green-beans':['potatoes'],
 'sheet-pan-gnocchi-white-beans-and-broccoli':['pasta','potatoes','legumes'],
};
export function normalizeSelection(value,options){
 const values=Array.isArray(value)?value:typeof value==='string'?[value]:[];
 return [...new Set(values.filter(item=>item!=='all'&&Object.hasOwn(options,item)))];
}
function selectedMatches(selection,value){return Array.isArray(selection)?!selection.length||selection.includes(value):selection==='all'||selection===value;}
export function normalizeMealStyles(value){
 const selected=normalizeSelection(value,{keto:true,nonketo:true,shared:true});
 const exclusive=selected.filter(item=>item!=='shared').at(-1);
 return selected.filter(item=>item==='shared'||item===exclusive);
}
export function toggleMealStyle(selected,value){
 if(selected.includes(value))return selected.filter(item=>item!==value);
 return normalizeMealStyles([...selected,value]);
}
export const applianceChoices={'Instant Pot':'Pressure cooker',Oven:'Oven',Pans:'Pans',Microwave:'Microwave','Two air fryers':'Air fryer',Blender:'Blender'};
export const defaultAppliances={'Instant Pot':1,Oven:1,Pans:1,Microwave:1,'Two air fryers':2,Blender:1};
export function availableAppliances(value){
 if(Array.isArray(value))return Object.fromEntries(Object.keys(applianceChoices).map(key=>[key,value.includes(key)?(key==='Two air fryers'?2:1):0]));
 if(value&&typeof value==='object')return Object.fromEntries(Object.keys(applianceChoices).map(key=>[key,Math.max(0,Math.min(['Instant Pot','Two air fryers'].includes(key)?2:1,Number.isInteger(value[key])?value[key]:defaultAppliances[key]))]));
 return {...defaultAppliances};
}
export function hasAppliances(recipe,inventory){
 return recipe.appliancesNeeded.every(key=>(inventory[key]||0)>=(key==='Two air fryers'?2:1)&&(key!=='Pans'||inventory.Oven>0));
}
export function matchesRecipe(recipe,servings,{protein='all',carb='all',starch='all',immune=false,iron=false,appliances=defaultAppliances}={}){
 const flags=nutrientFilters(recipe,servings);
 return hasAppliances(recipe,appliances)&&selectedMatches(protein,recipe.proteinType)&&selectedMatches(carb,recipe.group)&&(Array.isArray(starch)?!starch.length||starch.some(type=>recipeStarches[recipe.id]?.includes(type)):starch==='all'||recipeStarches[recipe.id]?.includes(starch))&&(!immune||flags.immune)&&(!iron||flags.iron);
}
