<script>
  import RecipeFlow from './RecipeFlow.svelte';
  import { recipeDocument } from './recipe-export.mjs';
  import { formatIngredient, purchaseNote } from './recipe-logic.mjs';
  import { cookText } from './display-units.mjs';
  let { recipes=[], settings, groceries=[], showShopping=false, shoppingOnly=false, chartOnly=false } = $props();
  const documents = $derived(shoppingOnly ? [] : recipes.map(recipe=>recipeDocument(recipe,settings)));
  const categories = [['produce','Vegetables & fruit'],['protein','Protein'],['dairy','Dairy & eggs'],['pantry','Pantry & seasonings']];
  const groups = {keto:'Keto',shared:'Keto main + family starch',nonketo:'Non-keto'};
  function macros(nutrition) { return `${Math.round(nutrition.kcal)} kcal · ${nutrition.protein_g.toFixed(1)} g protein · ${nutrition.carbs_g.toFixed(1)} g total carbohydrate · ${nutrition.fiber_g.toFixed(1)} g fiber · ${nutrition.net_carbs_g.toFixed(1)} g net carbohydrate`; }
</script>

<div class="print-document" class:chart-only={chartOnly} aria-label="Printable recipes and shopping list">
  {#if documents.length>1}<header class="packet-heading"><h1 class="print-title">Your dinner packet</h1><p>{documents.length} recipes · {settings.servings} adult servings each · {settings.units==='metric'?'Metric':'US'} cooking measures</p><p>Each recipe starts on a new page. Safe doneness and appliance capacity take priority over the time estimate.</p></header>{/if}
  {#each documents as document,i}
    <article class="print-meal" class:new-page={i>0} aria-label={document.title}>
      <h1 class="print-title">{document.title}</h1>
      <p class="meal-facts">{groups[document.group]||document.group} · {document.servings} adult servings · {document.units==='metric'?'Metric':'US'} measures · {document.activeMinutes} min active per original four-serving batch · {document.totalTime} total</p>
      {#if !chartOnly}<p>{document.summary}</p><p>{document.attentionSummary}</p>
      <p class="important">{document.capacity}</p><p>{document.timingNote}</p>
      <p class="small">{document.disclaimer}</p>{/if}
      <RecipeFlow recipe={recipes[i]} {settings}/>
      {#if !chartOnly}<h2>Ingredients</h2>
      <ul class="ingredient-list">{#each document.ingredients as ingredient}<li><strong>{ingredient.quantity}</strong> {ingredient.name}{#if ingredient.state||ingredient.note}<span class="ingredient-note">{[ingredient.state,ingredient.note].filter(Boolean).join(' · ')}</span>{/if}</li>{/each}</ul>
      {#if document.familyIngredient}<div class="family-starch"><h2>Separate family starch · {document.familyDiners} diners</h2><p><strong>{document.familyIngredient.quantity}</strong> {document.familyIngredient.name}</p><p>{document.familyIngredient.state} · {document.familyIngredient.note}</p></div>{:else if document.group==='shared'}<p>No family starch is included for this printout. The shared main serves all {document.servings} adults.</p>{/if}
      <h2>Before you start</h2><ul>{#each document.equipment as item}<li>{item}</li>{/each}</ul>
      <p>{document.safety}</p>
      <h2>Cook</h2><ol class="method-list">{#each document.steps as step}<li><strong>{step.title}</strong><p>{step.text}</p></li>{/each}</ol>
      <h2>Where your attention goes</h2><ul>{#each document.timeline as event}<li><strong>{event.phase} · {event.duration}</strong><p>{event.attention}</p></li>{/each}</ul><p class="small">Stages can overlap. Do not add every row as separate elapsed time. Safe endpoints and actual appliance behavior override the estimate.</p>
      {#if document.fallback}<h2>Capacity fallback</h2><p>{document.fallback}</p>{/if}
      <h2>Why this works</h2><p>{document.flavorRationale}</p><ul>{#each document.tips as tip}<li>{tip}</li>{/each}</ul>
      <h2>Estimated nutrition per adult</h2><p>{macros(document.nutrition)}</p>
      {#if document.familyNutrition}<p><strong>Family plate with selected starch:</strong> {macros(document.familyNutrition)}</p>{/if}
      <p class="small">{document.nutritionNote}</p>
      <p><strong>Listed allergens:</strong> {document.allergens.length?document.allergens.join(', '):'None in the specified ingredients'}. Check purchased labels and cross-contact.</p>
      <h2>First-cook checks</h2><ul>{#each document.limitations as limitation}<li>{limitation}</li>{/each}</ul>
      <h2>Leftovers</h2><p>{document.leftovers}</p>
      <h2>Sources</h2><ul class="source-list">{#each document.sources as source}<li>{source.title}<br/><a href={source.url}>{source.url}</a></li>{/each}</ul><p class="small">Sources support safety, labels or comparable methods. They do not validate this exact newly designed recipe.</p>
      {/if}
      {#if chartOnly}
      {#if document.familyIngredient}<p class="small"><strong>Separate family starch · {document.familyDiners} diners:</strong> {document.familyIngredient.quantity} {document.familyIngredient.name}. {document.familyIngredient.note}</p>{/if}
      <p class="small">{document.capacity} Timings are for the original four-serving batch. More food can need extra batches; keep settings, cut sizes and safe endpoints fixed.</p>
      <p class="small">Newly designed; not kitchen-tested. Read the complete method for label restrictions, equipment, capacity, safety and first-cook checks. Sources and estimated nutrition are in the full recipe.</p>
      {/if}
    </article>
  {/each}
  {#if showShopping||shoppingOnly}
    <section class="print-groceries" class:new-page={documents.length>0} aria-label="Printable shopping list">
      <h1 class="print-title">Your dinner shopping list</h1>
      <p>{recipes.length} dinners × {settings.servings} adult servings · {settings.units==='metric'?'Metric':'US'} measures. Shared dinners include the selected starch for {settings.familyDiners} non-keto diners each.</p>
      <h2>Dinners covered</h2><ul>{#each recipes as recipe}<li>{recipe.title}</li>{/each}</ul>
      {#each categories as [category,label]}{@const items=groceries.filter(item=>item.category===category)}{#if items.length}<section class="grocery-category"><h2>{label}</h2><ul class="grocery-list">{#each items as item}<li><span class="paper-checkbox" aria-hidden="true"></span><div><strong>{formatIngredient({...item,scale:'fixed'},4,settings.units)}</strong> {item.name}{#if item.state||item.note||purchaseNote({...item,scale:'fixed'},4)}<span class="ingredient-note">{cookText([item.state,item.note,purchaseNote({...item,scale:'fixed'},4)].filter(Boolean).join(' · '),settings.units)}</span>{/if}</div></li>{/each}</ul></section>{/if}{/each}
      <p>Amounts are edible ingredient totals, not package counts. Canned legumes are weighed after draining; buy enough cans for that yield. Raw and cooked foods stay separate. Check pantry ingredients before buying. Brand labels govern packaged sauces and bread.</p>
      <p>{settings.servings>4?'The shopping list covers all servings; cooking needs extra batches or verified larger cookware.':'Keep the recipe’s specified cut sizes, pan geometry and appliance liquid minimums.'}</p>
    </section>
  {/if}
</div>

<style>
  .print-document{display:none}
  @media print{
    .print-document{display:block!important; font:11pt/1.4 Georgia,serif!important;color:#000!important;background:#fff!important;overflow:visible!important;width:100%;max-width:none}
    .print-document :global(*){color:#000!important;background:transparent!important;box-shadow:none!important;border-radius:0!important;letter-spacing:normal!important}
    .print-document h1{font:700 20pt/1.15 Georgia,serif!important;margin:0 0 10pt!important;break-after:avoid}
    .print-document h2{font:700 13pt/1.2 Georgia,serif!important;margin:13pt 0 5pt!important;break-after:avoid}
    .print-document p{font-size:11pt!important;line-height:1.4!important;margin:4pt 0 8pt!important}
    .print-document ul,.print-document ol{margin:4pt 0 10pt!important;padding-left:18pt!important}
    .print-document li{font-size:11pt!important;line-height:1.4!important;margin:0 0 5pt!important;break-inside:avoid}
    .chart-only :global(.trn-view){margin:5pt 0!important}
    .chart-only :global(.trn-view h3){display:none!important}
    .chart-only :global(.trn-table){font-size:7.5pt!important;line-height:1.15!important}
    .chart-only :global(.trn-table th),.chart-only :global(.trn-table td){font-size:7.5pt!important;line-height:1.15!important;padding:2pt!important}
    .chart-only :global(.trn-ingredient .trn-state-detail){display:none!important}.chart-only :global(.trn-ingredient .trn-state-essential){font-size:7pt!important;line-height:1.1!important;margin-top:1pt!important}
    .chart-only .small{font-size:8pt!important;line-height:1.2!important;margin:3pt 0!important}
    .chart-only .meal-facts{font-size:9pt!important;line-height:1.2!important;margin:4pt 0!important}
    .chart-only .print-title{font-size:17pt!important}
    .print-document a{font-size:9pt!important;text-decoration:none!important;overflow-wrap:anywhere!important;word-break:break-word!important}
    .print-document .small,.print-document .ingredient-note{font-size:9pt!important;line-height:1.35!important}
    .ingredient-note{display:block;margin-top:2pt}
    .packet-heading{margin-bottom:18pt;border-bottom:1pt solid #777;padding-bottom:8pt}
    .important{border-left:2pt solid #555;padding-left:8pt}
    .family-starch{border-left:1pt solid #777;padding-left:8pt}
    .print-meal,.print-groceries{padding:0;margin:0;overflow:visible!important}
    .new-page{break-before:page}
    .method-list li p{margin-top:3pt!important}
    .grocery-list{list-style:none;padding-left:0!important}
    .grocery-list li{display:flex;align-items:start;gap:7pt}
    .paper-checkbox{display:inline-block;width:9pt;height:9pt;border:1pt solid #555;flex-shrink:0;margin-top:3pt}
  }
</style>
