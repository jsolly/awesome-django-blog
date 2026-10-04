import data from './nutrition-data.json' with {type:'json'};
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
  return {...nutrient,amount:observed?total:null,percent:observed?Math.round(total/nutrient.dailyValue*100):null};
 });
}
export function nutrientAmount(value){
 if(value===null)return '—';
 if(value===0)return '0';
 if(value<0.1)return '<0.1';
 return value<10?String(Math.round(value*10)/10):String(Math.round(value));
}
