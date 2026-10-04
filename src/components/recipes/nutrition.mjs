import data from './nutrition-data.json' with {type:'json'};
import {smoothieGlassesPerBatch} from './recipe-logic.mjs';
export const dailyNutrients = data.nutrients;
export function dailyNutrition(recipe, servings, scaledAmount) {
 const rows=data.recipes[recipe.id] || [];
 return dailyNutrients.map(nutrient=>{
  let total=0, observed=rows.length>0;
  for(const row of rows){
   if(!Number.isFinite(row.nutrients[nutrient.key])){observed=false;continue;}
   const ingredient=recipe.ingredients.find(i=>i.id===row.food);
   const factor=ingredient?.scale==='minimum' ? scaledAmount(ingredient,servings)/ingredient.amount : servings/4;
   total+=row.nutrients[nutrient.key]*row.grams/100*factor/servings;
  }
  if(recipe.type==='smoothie'){
   if(!Number.isFinite(recipe.estimatedYieldMl)||recipe.estimatedYieldMl<=0)observed=false;
   else total*=4/smoothieGlassesPerBatch(recipe);
  }
  return {...nutrient,amount:observed?total:null,percent:observed?Math.round(total/nutrient.dailyValue*100):null};
 });
}
export function nutrientAmount(value){
 if(value===null)return '—';
 if(value===0)return '0';
 if(value<0.1)return '<0.1';
 return value<10?String(Math.round(value*10)/10):String(Math.round(value));
}

// Count recorded omega-3 observations only; unobserved fatty acids cannot qualify a recipe.
export function recordedOmega3(recipe,servings,scaledAmount){
 let total=0;
 for(const row of data.recipes[recipe.id]||[]){
  const ingredient=recipe.ingredients.find(i=>i.id===row.food);
  const factor=ingredient?.scale==='minimum'?scaledAmount(ingredient,servings)/ingredient.amount:servings/4;
  total+=(row.omega3RecordedGramsPer100g||0)*row.grams/100*factor/servings;
 }
 return recipe.type==='smoothie'?total*4/smoothieGlassesPerBatch(recipe):total;
}
