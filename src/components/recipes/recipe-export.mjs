import {validateSettings,formatIngredient,servingNutrition,familyNutrition,capacityNote,purchaseNote} from './recipe-logic.mjs';
import {flowGrid,gridHtml} from './trn-logic.mjs';
import {cookText} from './display-units.mjs';
export const recipeDisclaimer='These newly designed recipes have not been cooked, tasted or stopwatch-tested. Nutrition is an ingredient estimate, not laboratory analysis. Sources support safety, labels or comparable methods; they do not validate this exact recipe.';
const leftovers='Refrigerate in shallow containers within two hours, or one hour above 90°F. Use within 3–4 days or freeze; reheat to 165°F. Keep cold greens and yogurt separate.';
/** One cooking document drives print and assistant exports. Model weights stay in recipes.json. */
export function recipeDocument(recipe, settings={}) {
 const valid=validateSettings(settings);
 const {servings,units}=valid;
 const familyDiners=recipe.group==='shared'?valid.familyDiners:0;
 const option=familyDiners>0 ? recipe.familyOptions.find(o=>o.id===settings.familyChoice?.[recipe.id])||recipe.familyOptions[0] : null;
 const text=value=>cookText(value||'',units);
 const grid=flowGrid(recipe,valid);
 const ingredients=recipe.ingredients.map(i=>({quantity:formatIngredient(i,servings,units),name:i.name,state:text(i.state),note:text([i.note,purchaseNote(i,servings)].filter(Boolean).join(' · '))}));
 const familyIngredient=option?{quantity:formatIngredient({...option,amount:option.amount*familyDiners,us:option.us?{...option.us,amount:option.us.amount*familyDiners}:undefined,scale:'fixed'},4,units),name:option.ingredientName,state:text(option.state),note:text(option.note),choiceId:option.id}:null;
 return {recipeId:recipe.id,title:recipe.title,group:recipe.group,servings,units,familyDiners,
  cookingFlow:{notation:'Tabular Recipe Notation (TRN)',prep:grid.prep,columns:grid.columns,rows:grid.rows.map(r=>r.cells)},
  summary:recipe.summary,activeMinutes:recipe.activeMinutes,
  totalTime:`${recipe.totalMin}–${recipe.totalMax}${servings>4?'+':''} min${servings>4?' / base batch':''}${recipe.timeVariable?' expected; pressure buildup can take longer':''}`,
  attentionSummary:recipe.attentionSummary,capacity:text(capacityNote(servings)),
  timingNote:'Ingredients are scaled; keep food thickness, spacing, settings and safe endpoints fixed. Timings assume the four-serving batch and specified shortcuts. More food can require additional batches.',
  equipment:recipe.equipment.map(text),ingredients,familyIngredient,
  familyOptions:recipe.familyOptions.map(o=>({choiceId:o.id,label:o.label,quantityPerPerson:formatIngredient({...o,scale:'fixed'},4,units),name:o.ingredientName,state:text(o.state),note:text(o.note),nutritionAddedPerPerson:{...o.nutrition},allergens:[...(o.allergens||[])]})),
  steps:recipe.steps.map(s=>({title:s.title,text:text(s.text)})),
  timeline:recipe.timeline.map(e=>({phase:e.phase,duration:text(e.duration),attention:text(e.attention)})),
  tips:recipe.tips.map(text),fallback:text(recipe.fallback),limitations:recipe.limitations.map(text),sources:recipe.sources.map(s=>({...s})),
  nutrition:servingNutrition(recipe,servings),familyNutrition:option?familyNutrition(recipe,option.id,servings):null,
  nutritionNote:'Per adult: base includes measured sauces, seeds and sides. Family nutrition adds one selected starch portion. US net carbs = total carbohydrate − fiber. Labels and food variation matter; no guarantee of ketosis.',
  allergens:[...new Set([...recipe.allergens,...(option?.allergens||[])])],
  flavorRationale:recipe.flavorRationale,disclaimer:recipeDisclaimer,leftovers:text(leftovers),
  safety:'Prepare cold sides first. Keep raw-poultry tools separate; use clean serving utensils. Probe more than one thick piece. A timer is not a doneness test.',
  image:recipe.image?{...recipe.image}:null,
 };
}
const macros=n=>`${Math.round(n.kcal)} kcal; ${n.protein_g.toFixed(1)} g protein; ${n.carbs_g.toFixed(1)} g total carbs; ${n.fiber_g.toFixed(1)} g fiber; ${n.net_carbs_g.toFixed(1)} g net carbs`;
export function documentMarkdown(d,headingLevel=1){
 const lines=[`# ${d.title}`,`${d.servings} adult servings · ${d.units==='metric'?'Metric':'US'} measures · ${d.group} · ${d.activeMinutes} min active per base batch · ${d.totalTime}`,d.summary,d.attentionSummary,d.capacity,d.timingNote,'## Cooking flow (Tabular Recipe Notation)',gridHtml(d.title,{...d.cookingFlow,rows:d.cookingFlow.rows.map(cells=>({cells}))}),'## Ingredients',...d.ingredients.map(i=>`- ${i.quantity} ${i.name}${i.state?' — '+i.state:''}${i.note?'. '+i.note:''}`)];
 if(d.familyIngredient)lines.push(`## Separate family starch for ${d.familyDiners} diners`,`${d.familyIngredient.quantity} ${d.familyIngredient.name} — ${d.familyIngredient.state}. ${d.familyIngredient.note}`);
 if(d.familyOptions.length)lines.push('## Family starch options (per non-keto adult)',...d.familyOptions.map(o=>`- ${o.label}: ${o.quantityPerPerson} ${o.name} — ${o.state}. ${o.note}`));
 lines.push('## Equipment',...d.equipment.map(x=>'- '+x),'## Cook',d.safety,...d.steps.map((s,i)=>`${i+1}. **${s.title}.** ${s.text}`),'## Attention timeline',...d.timeline.map(e=>`- ${e.phase}: ${e.duration}. ${e.attention}`),'Stages can overlap; endpoints and appliance behavior override the estimate.','## Flavor and capacity',d.flavorRationale,...d.tips.map(t=>'- '+t),d.fallback,'## Estimated nutrition per adult',macros(d.nutrition));
 if(d.familyNutrition)lines.push('With selected family starch: '+macros(d.familyNutrition));
 lines.push(d.nutritionNote,`Known allergens for these plates: ${d.allergens.join(', ')||'none listed; check every product label'}. Check product labels and cross-contact.`,'## First-cook checks and limits',...d.limitations.map(x=>'- '+x),'## Leftovers',d.leftovers,'## Sources',...d.sources.map(s=>`- [${s.title}](${s.url})`),d.disclaimer);
 return lines.filter(Boolean).map(line=>line.replace(/^(#{1,6}) /gm,(_,marks)=>'#'.repeat(marks.length+headingLevel-1)+' ')).join('\n\n')+'\n';
}
export function recipeBrief(recipe,settings={}){return documentMarkdown(recipeDocument(recipe,settings));}
export function recipeBundle(recipes,settings={}){
 return {schemaVersion:1,baseServings:4,settings:validateSettings(settings),disclaimer:recipeDisclaimer,measurementPolicy:'Small seasoning and finishing amounts use spoon measures even in metric mode. Internal model weights are estimates, not a requirement to weigh tiny amounts.',recipes:recipes.map(r=>recipeDocument(r,settings))};
}
