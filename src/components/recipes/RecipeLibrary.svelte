<script>
  import { onMount, tick } from 'svelte';
  import RecipePrint from './RecipePrint.svelte';
  import RecipeFlow from './RecipeFlow.svelte';
  import {recipeBrief,recipeBundle} from './recipe-export.mjs';
  import {cookText} from './display-units.mjs';
  import { filterRecipes, formatIngredient, formatQuantity, shoppingList, familyNutrition, capacityNote, temperature, validateSettings, servingNutrition, purchaseNote } from './recipe-logic.mjs';
  let { recipes, headingTag='h1' } = $props();
  const groups = { keto: 'Keto', shared: 'Shared main', nonketo: 'Non-keto' };
  const appliances = { 'air-fryer': 'Two air fryers', oven: 'Oven', 'instant-pot': 'Instant Pot' };
  const defaults = { query:'', group:'', appliance:'', maxActive:0, maxTotal:0, maxInterventions:-1, proteinType:'', avoidAllergens:[], booster:'', sort:'active' };
  let filters = $state({...defaults});
  let servings = $state(4);
  let units = $state('us');
  let familyDiners = $state(2);
  let familyChoice = $state({});
  let selectedIds = $state([]);
  let recipeId = $state('');
  let ingredientChecks = $state([]);
  let stepChecks = $state([]);
  let shoppingChecks = $state([]);
  let hydrated = $state(false);
  let cookingFocus = $state(false);
  let printMode = $state('auto');
  let printPrepared = $state(false);
  let previousPrintAttribute = null;
  let ownsPrintAttribute = false;
  let libraryElement=$state(null);
  let message = $state('');
  let detailHeading=$state(null);
  let listHeading=$state(null);
  const results = $derived(filterRecipes(recipes, {...filters,familyDiners,familyChoice}));
  const current = $derived(recipes.find(r => r.id === recipeId));
  const groceries = $derived(shoppingList(recipes, selectedIds, {servings, familyDiners, familyChoice}));
  const selected = $derived(recipes.filter(r => selectedIds.includes(r.id)));
  const printSettings = $derived({servings,units,familyDiners,familyChoice});
  const effectivePrintMode = $derived(printMode==='auto' ? (current ? 'recipe' : selected.length ? 'plan' : 'all') : printMode);
  const printRecipes = $derived(['recipe','chart'].includes(effectivePrintMode)&&current ? [current] : effectivePrintMode==='all' ? recipes : selected);
  const printGroceries = $derived(shoppingList(recipes, printRecipes.map(r=>r.id), {servings,familyDiners,familyChoice}));
  const baseNutrition = $derived(current ? servingNutrition(current,servings) : null);
  const family = $derived(current?.familyOptions?.length ? familyNutrition(current, choiceFor(current),servings) : null);
  const groceryCategories = ['produce','protein','dairy','pantry'];
  const categoryLabels = {produce:'Vegetables & fruit', protein:'Protein', dairy:'Dairy & eggs', pantry:'Pantry & seasonings'};
  const storageKey = 'blogthedata-meals-v1';

  function choiceFor(recipe) { return recipe.familyOptions?.find(o=>o.id===familyChoice[recipe.id])?.id || recipe.familyOptions?.[0]?.id || ''; }
  function groceryKey(item) {return JSON.stringify([item.id,item.state,item.unit]);}
  function displayTime(recipe) { return servings > 4 ? `${recipe.totalMin}–${recipe.totalMax}+ min / batch` : `${recipe.totalMin}–${recipe.totalMax} min${recipe.timeVariable ? ' expected' : ''}`; }
  function togglePlan(id) { selectedIds = selectedIds.includes(id) ? selectedIds.filter(x=>x!==id) : [...selectedIds,id]; shoppingChecks=[]; }
  function toggleCheck(list,id) { return list.includes(id) ? list.filter(x=>x!==id) : [...list,id]; }
  function setServings(value) { const valid = validateSettings({servings:Number(value),familyDiners,units}); servings=valid.servings; familyDiners=valid.familyDiners; shoppingChecks=[]; }
  function setFamily(value) { familyDiners=validateSettings({servings,familyDiners:Number(value),units}).familyDiners; shoppingChecks=[]; }
  function setChoice(id,value) { familyChoice={...familyChoice,[id]:value}; shoppingChecks=[]; }
  function avoid(value) { filters={...filters,avoidAllergens:toggleCheck(filters.avoidAllergens,value)}; }
  function resetFilters() { filters={...defaults,avoidAllergens:[]}; }
  async function openRecipe(id,scroll=true) {
    recipeId=id;assistantText='';ingredientChecks=[];stepChecks=[];cookingFocus=false;message='';
    await tick();
    if(scroll && detailHeading) {detailHeading.focus({preventScroll:true}); detailHeading.scrollIntoView({behavior:'auto',block:'start'});}
  }
  async function toggleCookingView(){cookingFocus=!cookingFocus;await tick();detailHeading?.focus({preventScroll:true});detailHeading?.scrollIntoView({block:'start'});}
  async function backToResults() { cookingFocus=false; await tick(); listHeading?.focus({preventScroll:true});listHeading?.scrollIntoView({block:'start'}); }
  function readURL() {
    const p = new URLSearchParams(window.location.search);
    const allowed = (key,choices) => choices.includes(p.get(key)) ? p.get(key) : '';
    filters={...defaults,query:(p.get('q')||'').slice(0,200),group:allowed('group',['keto','shared','nonketo']),appliance:allowed('appliance',['air-fryer','oven','instant-pot']),proteinType:allowed('protein',['fish','chicken','turkey','vegetarian','plant-forward']),booster:allowed('booster',['hemp','flax','yeast']),sort:allowed('sort',['active','total','protein'])||'active',maxActive:[0,10,12,15].includes(Number(p.get('active')))?Number(p.get('active')):0,maxInterventions:p.has('attention')&&[-1,0,1,2].includes(Number(p.get('attention')))?Number(p.get('attention')):-1,maxTotal:[0,25,35,40,45].includes(Number(p.get('total')))?Number(p.get('total')):0,avoidAllergens:(p.get('avoid')||'').split(',').filter(x=>['milk','egg','fish','wheat','tree-nuts'].includes(x))};
    const settings=validateSettings({servings:p.get('servings')===null?servings:Number(p.get('servings')),familyDiners:p.get('family')===null?familyDiners:Number(p.get('family')),units:p.get('units')||units});
    servings=settings.servings;familyDiners=settings.familyDiners;units=settings.units;
    const choices={};for(const part of (p.get('starch')||'').split(',')){const [rid,oid]=part.split(':');if(recipes.find(r=>r.id===rid)?.familyOptions.some(o=>o.id===oid))choices[rid]=oid;}familyChoice={...familyChoice,...choices};
    const id=window.location.hash.slice(1);
    if(recipes.some(r=>r.id===id))recipeId=id;
  }
  function shareURL() {
    const p=new URLSearchParams();
    if(filters.query)p.set('q',filters.query);
    for(const [k,v] of [['group',filters.group],['appliance',filters.appliance],['protein',filters.proteinType],['booster',filters.booster]])if(v)p.set(k,v);
    if(filters.maxInterventions>=0)p.set('attention',String(filters.maxInterventions));
    if(filters.maxActive)p.set('active',String(filters.maxActive));if(filters.maxTotal)p.set('total',String(filters.maxTotal));
    if(filters.sort!=='active')p.set('sort',filters.sort);if(filters.avoidAllergens.length)p.set('avoid',filters.avoidAllergens.join(','));
    const choices=recipes.filter(r=>r.familyOptions.length).map(r=>`${r.id}:${choiceFor(r)}`).join(',');if(choices)p.set('starch',choices);
    p.set('servings',String(servings));p.set('units',units);p.set('family',String(familyDiners));
    const url=new URL(window.location.href);url.search=p.toString();url.hash=recipeId;return url.href;
  }
  async function copyLink() {
    const link=shareURL();
    try {window.history.replaceState(null,'',link);}catch {/* Sharing still works when history is unavailable. */}
    try {await navigator.clipboard.writeText(link);message='Recipe and filter link copied.';}catch {message='Copy the address from your browser to share these settings.';}
  }
  function preparePrint() {
    if (!ownsPrintAttribute) { previousPrintAttribute=document.documentElement.getAttribute('data-recipe-print'); ownsPrintAttribute=true; }
    document.documentElement.setAttribute('data-recipe-print',effectivePrintMode);
    printPrepared=true;
  }
  function restorePrint() {
    if (ownsPrintAttribute) {
      if(previousPrintAttribute===null)document.documentElement.removeAttribute('data-recipe-print');
      else document.documentElement.setAttribute('data-recipe-print',previousPrintAttribute);
    }
    ownsPrintAttribute=false;printPrepared=false;printMode='auto';
  }
  async function print(target) {
    printMode=target;await tick();preparePrint();await tick();
    try { window.print(); } catch { restorePrint();message='Printing could not open. Use your browser’s Print command.'; }
  }
  let assistantText = $state('');
  async function copyCookingBrief() {
    if(!current)return;
    const brief=recipeBrief(current,{servings,units,familyDiners,familyChoice});
    try {await navigator.clipboard.writeText(brief);assistantText='';message='Complete cooking brief copied with your servings, units and family starch.';}
    catch {assistantText=brief;message='Clipboard is unavailable. Select and copy the cooking brief below.';}
  }
  function downloadRecipeData(all=false) {
    const content=recipeBundle(all?recipes:current?[current]:[],{servings,units,familyDiners,familyChoice});
    const url=URL.createObjectURL(new Blob([JSON.stringify(content,null,2)+'\n'],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download=all?'recipe-library.json':`${current.id}-${servings}-servings.json`;
    link.click();window.setTimeout(()=>URL.revokeObjectURL(url),1000);
    message='Structured recipe data downloaded with your current settings.';
  }
  function textInUnits(text) {return cookText(text,units);}
  onMount(()=>{
    try { const saved=JSON.parse(localStorage.getItem(storageKey)||'null'); if(saved && typeof saved==='object') {const s=validateSettings(saved);servings=s.servings;familyDiners=s.familyDiners;units=s.units;selectedIds=Array.isArray(saved.selectedIds)?saved.selectedIds.filter(id=>recipes.some(r=>r.id===id)):[];familyChoice=saved.familyChoice&&typeof saved.familyChoice==='object'?saved.familyChoice:{};} } catch {/* Reading remains usable without storage. */}
    readURL();hydrated=true;if(recipeId)void tick().then(()=>{detailHeading?.focus({preventScroll:true});detailHeading?.scrollIntoView({block:'start'});});
    window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',restorePrint);
    const hash=()=>{const id=window.location.hash.slice(1);if(recipes.some(r=>r.id===id))void openRecipe(id,true);};window.addEventListener('hashchange',hash);
    return()=>{window.removeEventListener('hashchange',hash);window.removeEventListener('beforeprint',preparePrint);window.removeEventListener('afterprint',restorePrint);restorePrint();};
  });
  $effect(()=>{if(hydrated){try{localStorage.setItem(storageKey,JSON.stringify({servings,familyDiners,units,selectedIds,familyChoice}));}catch {/* No persistence required to cook. */}}});
</script>

<section class="meal-library" class:cookingFocus data-hydrated={hydrated} data-print-prepared={printPrepared} bind:this={libraryElement} aria-label="Fast dinner library">
  <div class="library-intro">
    <p class="eyebrow">12 DINNERS · THREE WAYS TO EAT</p>
    <svelte:element this={headingTag} class="library-title">Fast dinners,<br/>less watching.</svelte:element>
    <p class="fine image-disclosure">Meal images are AI-generated illustrations, not photographs of tested recipes or portion guides.</p>
    <p class="lead">Pick a meal that fits tonight. Scale the ingredients, keep family starches separate, and let the appliance do most of the work.</p>
    <button type="button" class="outline" disabled={!hydrated} onclick={()=>print('all')}>Print all 12 recipes</button>
    <div class="assistant-downloads"><p>For an assistant: <a href="/data/recipe-library.json" download>four-serving recipe data (JSON)</a> · <a href="/data/recipe-library.md" download>complete cooking guide (Markdown)</a>. Each open recipe also has a cooking brief and JSON export using your settings.</p><button type="button" class="outline" disabled={!hydrated} onclick={()=>downloadRecipeData(true)}>Download all recipes with my settings</button></div>
    <div class="intro-facts"><span>8–15 min active</span><span>No initial sauté</span><span>Protein + vegetables</span></div>
    <p class="evidence-note">Newly designed, independently reviewed recipes. Nutrition is calculated; flavor, fit and timing still need a first cook.</p>
  </div>

  <div class="browse" id="meal-results">
    <div class="section-top"><h2 bind:this={listHeading} tabindex="-1">Find tonight’s dinner</h2><a href="#how-to-cook">Learn the method ↓</a></div>
    <div class="filter-box">
      <div class="group-buttons" aria-label="Meal group">
        {#each [['','All dinners'],['keto','Keto'],['shared','Keto + family'],['nonketo','Non-keto']] as [value,label]}
          <button type="button" class:chosen={filters.group===value} aria-pressed={filters.group===value} disabled={!hydrated} onclick={()=>filters={...filters,group:value}}>{label}</button>
        {/each}
      </div>
      <div class="primary-filters">
        <label class="search-label">Search meals or ingredients<input type="search" placeholder="Chicken, broccoli, hemp…" bind:value={filters.query} maxlength="200" disabled={!hydrated}/></label>
        <label>Appliance<select aria-label="Appliance" bind:value={filters.appliance} disabled={!hydrated}><option value="">Any appliance</option><option value="air-fryer">Two air fryers</option><option value="oven">Oven</option><option value="instant-pot">Instant Pot</option></select></label>
        <label>{servings>4?'Hands-on per batch':'Hands-on'}<select aria-label={servings>4?'Hands-on per batch':'Hands-on'} bind:value={filters.maxActive} disabled={!hydrated}><option value={0}>Any active time</option><option value={10}>Up to 10 min</option><option value={12}>Up to 12 min</option><option value={15}>Up to 15 min</option></select></label>
        <label>{servings>4?'Time per batch':'Time to dinner'}<select aria-label={servings>4?'Time per batch':'Time to dinner'} bind:value={filters.maxTotal} disabled={!hydrated}><option value={0}>Any total time</option><option value={25}>Up to 25 min</option><option value={35}>Up to 35 min</option><option value={40}>Up to 40 min</option><option value={45}>Up to 45 min</option></select></label>
      </div>
      <details class="extra-filters"><summary>Protein, boosters & ingredient exclusions</summary>
        <div class="secondary-filters">
          <label>Protein<select aria-label="Protein" bind:value={filters.proteinType} disabled={!hydrated}><option value="">Any protein</option><option value="fish">Fish</option><option value="chicken">Chicken</option><option value="turkey">Turkey</option><option value="vegetarian">Vegetarian as specified</option><option value="plant-forward">Plant-forward</option></select></label>
          <label>Booster<select aria-label="Booster" bind:value={filters.booster} disabled={!hydrated}><option value="">Any / none</option><option value="hemp">Hemp hearts</option><option value="flax">Ground flax</option><option value="yeast">Nutritional yeast</option></select></label>
          <label>Scheduled main-appliance actions<select aria-label="Scheduled main-appliance actions" bind:value={filters.maxInterventions} disabled={!hydrated}><option value={-1}>Any attention level</option><option value={0}>No scheduled main-appliance action</option><option value={1}>At most one</option><option value={2}>At most two</option></select></label>
          <fieldset><legend>Exclude listed allergens</legend><div class="check-row">{#each [['milk','Milk'],['egg','Egg'],['fish','Fish'],['wheat','Wheat'],['tree-nuts','Tree nuts']] as [value,label]}<label><input type="checkbox" checked={filters.avoidAllergens.includes(value)} onchange={()=>avoid(value)} disabled={!hydrated}/>{label}</label>{/each}</div></fieldset>
        </div>
        <p class="fine">These exclusions include the selected family starch when non-keto diners are above zero, and match known ingredients, not cross-contact or every brand. Check all purchased labels. Vegetarian Parmesan must use suitable rennet.</p>
      </details>
      <p class="fine">This action filter counts scheduled starts, shakes, flips or additions to the main cooking appliances. Cold sides and heating family starches still need active work. Separate component removals and final doneness checks always remain; optional rack swaps depend on the oven. Time filters use the upper estimate and omit the variable-pressure dinner. For more than four servings, allow extra batches; displayed time is per batch.</p>
      <div class="results-toolbar"><p role="status" aria-live="polite">{results.length} of {recipes.length} dinners</p><label>Sort<select aria-label="Sort" bind:value={filters.sort} disabled={!hydrated}><option value="active">Least hands-on</option><option value="total">Fastest total</option><option value="protein">Most protein</option></select></label><button class="text-button" type="button" disabled={!hydrated} onclick={resetFilters}>Reset filters</button></div>
    </div>
    <div class="household-settings"><div><strong>Your table</strong><span>Applies to all recipes and your shopping list</span></div>
      <label>Adult servings<select aria-label="Adult servings" value={servings} onchange={e=>setServings(e.currentTarget.value)} disabled={!hydrated}>{#each [2,4,6,8] as n}<option value={n}>{n}</option>{/each}</select></label>
      <label>Measurements<select aria-label="Measurements" bind:value={units} disabled={!hydrated}><option value="us">US</option><option value="metric">Metric</option></select></label>
      <label>Non-keto diners <span>(shared meals)</span><select aria-label="Non-keto diners (shared meals)" value={familyDiners} onchange={e=>setFamily(e.currentTarget.value)} disabled={!hydrated}>{#each Array.from({length:servings+1},(_,i)=>i) as n}<option value={n}>{n}</option>{/each}</select></label>
    </div>
    {#if servings!==4}<p class="capacity-alert">{capacityNote(servings)}</p>{/if}
    {#if !results.length}<div class="empty"><h3>No dinner matches those choices.</h3><p>Relax the time limit, choose another appliance, or clear an exclusion.</p><button type="button" onclick={resetFilters}>Show all dinners</button></div>{/if}
    <div class="recipe-grid">
      {#each results as recipe (recipe.id)}
        <article class="recipe-card" class:planned={selectedIds.includes(recipe.id)}>
          <div class="card-top"><span class="badge" class:shared={recipe.group==='shared'} class:nonketo={recipe.group==='nonketo'}>{groups[recipe.group]}</span><span class="appliance">{appliances[recipe.appliance]}</span></div>
          {#if recipe.image}<figure class="card-photo"><img src={recipe.image.cardSrc} srcset={recipe.image.cardSrcset} sizes="(max-width:600px) 340px, (max-width:1000px) 420px, 360px" width={recipe.image.width} height={recipe.image.height} alt={recipe.image.alt} loading="lazy" decoding="async"/><figcaption>AI illustration{recipe.group==='shared'?' · keto base':''}</figcaption></figure>{/if}
          <h3><button type="button" class="title-button" disabled={!hydrated} onclick={()=>openRecipe(recipe.id)}>{recipe.title}</button></h3>
          <p class="card-summary">{recipe.summary}</p>
          <dl class="card-numbers"><div><dt>Active</dt><dd>{recipe.activeMinutes}{servings>4?'+':''} min</dd></div><div><dt>Total</dt><dd>{displayTime(recipe)}</dd></div><div><dt>Protein</dt><dd>{Math.round(servingNutrition(recipe,servings).protein_g)} g</dd></div></dl>
          <p class="attention">{recipe.attentionSummary}</p>
          <div class="card-actions"><button class="open-button" type="button" disabled={!hydrated} onclick={()=>openRecipe(recipe.id)}>See recipe <span aria-hidden="true">↗</span></button><label><input type="checkbox" checked={selectedIds.includes(recipe.id)} onchange={()=>togglePlan(recipe.id)} disabled={!hydrated}/><span>Add to plan<span class="sr-only">: {recipe.title}</span></span></label></div>
        </article>
      {/each}
    </div>
    {#if selected.length}<div class="plan-bar"><span><strong>{selected.length} {selected.length===1?'dinner':'dinners'}</strong> in your plan · {servings} adult servings each</span><a href="#shopping-list">See shopping list ↓</a></div>{/if}
  </div>

  {#if current}
    <section class="recipe-detail" id={current.id} aria-labelledby="recipe-detail-title">
      <div class="detail-toolbar"><button type="button" class="text-button" onclick={backToResults}>← Back to dinners</button><div><button type="button" class="outline" onclick={toggleCookingView}>{cookingFocus?'Exit cooking view':'Cooking view'}</button><button type="button" class="outline" onclick={()=>print('chart')}>Print cooking chart</button><button type="button" class="outline" onclick={()=>print('recipe')}>Print recipe</button><button type="button" class="outline" onclick={copyLink}>Copy link</button><button type="button" class="outline" onclick={copyCookingBrief}>Copy cooking brief</button><button type="button" class="outline" onclick={()=>downloadRecipeData()}>Download recipe JSON</button></div></div>
      <p class="eyebrow">{groups[current.group]} · {appliances[current.appliance]}</p>
      <h2 id="recipe-detail-title" tabindex="-1" bind:this={detailHeading}>{current.title}</h2>
      <p class="detail-summary">{current.summary}</p>
      {#if assistantText}<label class="assistant-copy">Cooking brief · select and copy<textarea readonly rows="12" value={assistantText} aria-label="Cooking brief to copy"></textarea></label>{/if}
      <div class="detail-facts"><span><strong>{current.activeMinutes}{servings>4?'+':''} min</strong> active{servings>4?' / base batch':''}</span><span><strong>{displayTime(current)}</strong> total</span><span><strong>{servings}</strong> adult servings</span></div>
      {#if current.image}<figure class="recipe-photo"><img src={current.image.src} srcset={current.image.detailSrcset} sizes="(max-width:600px) 320px, (max-width:1000px) 680px, 960px" width={current.image.width} height={current.image.height} alt={current.image.alt} loading="eager" decoding="async"/><figcaption>{current.image.caption}</figcaption></figure>{/if}
      {#if !results.some(r=>r.id===current.id)}<p class="capacity-alert">This open recipe does not match your current filters. Its ingredients are shown in full.</p>{/if}
      {#if current.timeVariable}<p class="capacity-alert">Pressure building can take longer. This is an expected range, not a firm deadline.</p>{/if}
      {#if servings!==4}<p class="capacity-alert">{capacityNote(servings)}</p>{/if}
      <p class="fine">Ingredients below are scaled. Keep cut sizes, appliance settings and safe temperatures fixed. Timings assume the original four-serving batch and specified shortcuts.</p>
      {#if current.familyOptions.length}
        <div class="family-box"><h3>One main, two kinds of plate</h3><p>Keep starch separate. The keto base stays the same; add one starch portion for each of the {familyDiners} non-keto {familyDiners===1?'diner':'diners'}.</p><label>Family starch<select aria-label="Family starch" value={choiceFor(current)} onchange={e=>setChoice(current.id,e.currentTarget.value)}>{#each current.familyOptions as option}<option value={option.id}>{option.label}</option>{/each}</select></label>{#if familyDiners===0}<p class="fine">No family starch is added to your shopping list.</p>{/if}</div>
      {/if}
      <RecipeFlow recipe={current} settings={printSettings}/><div class="detail-columns"><div class="ingredient-panel"><h3>Ingredients · {servings} servings</h3><ul class="ingredients">
        {#each current.ingredients as ingredient,i}<li class:checked={ingredientChecks.includes(i)}><label><input type="checkbox" checked={ingredientChecks.includes(i)} onchange={()=>ingredientChecks=toggleCheck(ingredientChecks,i)}/><span><strong>{formatIngredient(ingredient,servings,units)}</strong> {ingredient.name}<small>{textInUnits([ingredient.state,ingredient.note,purchaseNote(ingredient,servings)].filter(Boolean).join(' · '))}</small></span></label></li>{/each}
      </ul>
      {#if current.familyOptions.length && familyDiners>0}{@const option=current.familyOptions.find(o=>o.id===choiceFor(current))||current.familyOptions[0]}<div class="family-ingredient"><strong>Family starch · {familyDiners} diners</strong><p>{formatIngredient({...option,us:option.us ? {...option.us,amount:option.us.amount*familyDiners}:undefined,amount:option.amount*familyDiners,scale:'fixed'},4,units)} {option.ingredientName}</p><small>{option.note}</small></div>{/if}
      <details class="nutrition" open><summary>Estimated nutrition per adult</summary><p class="fine">Base meal, including measured sauces, seeds and sides. Serving scaling keeps the same food portion size; fixed minimum broth is recalculated for smaller batches.</p><dl><div><dt>Calories</dt><dd>{Math.round(baseNutrition.kcal)} kcal</dd></div><div><dt>Protein</dt><dd>{baseNutrition.protein_g.toFixed(1)} g</dd></div><div><dt>Total carbs</dt><dd>{baseNutrition.carbs_g.toFixed(1)} g</dd></div><div><dt>Fiber</dt><dd>{baseNutrition.fiber_g.toFixed(1)} g</dd></div><div><dt>Net carbs</dt><dd>{baseNutrition.net_carbs_g.toFixed(1)} g</dd></div></dl>{#if family && familyDiners>0}<p class="family-macros"><strong>Family plate with selected starch:</strong> {Math.round(family.kcal)} kcal · {family.protein_g.toFixed(1)} g protein · {family.carbs_g.toFixed(1)} g total carbs · {family.net_carbs_g.toFixed(1)} g net carbs.</p>{/if}<p class="fine">US net carbs = total carbohydrate − fiber. Brand and food variation matter. This does not guarantee ketosis.</p></details>
      </div><div class="method-panel"><h3>Before you start</h3><ul class="equipment">{#each current.equipment as item}<li>{textInUnits(item)}</li>{/each}</ul><p class="safe-note">Prepare cold sides first. Keep raw-poultry tools separate, use clean serving utensils, and probe more than one thick piece. A timer is not a doneness test.</p><h3>Cook</h3><ol class="steps">{#each current.steps as step,i}<li class:checked={stepChecks.includes(i)}><label><input type="checkbox" checked={stepChecks.includes(i)} onchange={()=>stepChecks=toggleCheck(stepChecks,i)}/><span><strong>{step.title}</strong><span>{textInUnits(step.text)}</span></span></label></li>{/each}</ol>
      <h3>Where your attention goes</h3><div class="timeline">{#each current.timeline as event}<div><strong>{event.phase}</strong><span>{textInUnits(event.duration)}</span><p>{textInUnits(event.attention)}</p></div>{/each}</div><p class="fine">Stages can overlap; do not add every row as separate elapsed time. Safe endpoints and actual appliance behavior override the estimate.</p>
      {#if current.fallback}<details open><summary>Capacity fallback</summary><p>{textInUnits(current.fallback)}</p></details>{/if}
      <details open><summary>Why this works</summary><p>{current.flavorRationale}</p><ul>{#each current.tips as tip}<li>{textInUnits(tip)}</li>{/each}</ul></details>
      <details><summary>Sources & first-cook checks</summary><ul>{#each current.limitations as note}<li>{textInUnits(note)}</li>{/each}</ul><ul>{#each current.sources as source}<li><a href={source.url} rel="noopener noreferrer">{source.title}</a></li>{/each}</ul><p class="fine">Sources support safety, labels or comparable methods. They do not validate this exact newly designed recipe.</p></details>
      </div></div>
      <div class="detail-bottom"><button type="button" onclick={()=>togglePlan(current.id)}>{selectedIds.includes(current.id)?'Remove from plan':'Add this dinner to plan'}</button><button type="button" class="text-button" onclick={()=>{ingredientChecks=[];stepChecks=[];}}>Reset cooking checks</button></div>
    </section>
  {/if}

  <section class="shopping-section" id="shopping-list" aria-labelledby="shopping-title"><div class="section-top"><div><p class="eyebrow">A FEW NIGHTS, ONE LIST</p><h2 id="shopping-title">Your dinner plan</h2></div>{#if selected.length}<div class="print-plan-actions"><button type="button" class="outline" onclick={()=>print('plan')}>Print dinner packet</button><button type="button" class="outline" onclick={()=>print('shopping')}>Print shopping list</button></div>{/if}</div>
    {#if !selected.length}<p>Select “Add to plan” on a dinner to combine its ingredients here. Your plan stays in this browser when storage is available.</p>{:else}
      <p>{selected.length} dinners × {servings} adult servings. Shared dinners include starch for {familyDiners} non-keto diners each.</p>
      <ul class="planned-meals">{#each selected as recipe}<li><span>{recipe.title}</span>{#if recipe.familyOptions.length}<label><span class="sr-only">Starch for {recipe.title}</span><select value={choiceFor(recipe)} onchange={e=>setChoice(recipe.id,e.currentTarget.value)}>{#each recipe.familyOptions as option}<option value={option.id}>{option.label}</option>{/each}</select></label>{/if}<button type="button" class="text-button" onclick={()=>togglePlan(recipe.id)} aria-label={`Remove ${recipe.title} from plan`}>Remove</button></li>{/each}</ul>
      {#if servings>4}<p class="capacity-alert">This list covers all servings. Cooking takes additional batches or larger verified cookware; no extra total-time promise is made.</p>{/if}
      <div class="grocery-grid">{#each groceryCategories as category}{@const items=groceries.filter(item=>item.category===category)}{#if items.length}<section><h3>{categoryLabels[category]}</h3><ul class="groceries">{#each items as item}<li class:checked={shoppingChecks.includes(groceryKey(item))}><label><input type="checkbox" checked={shoppingChecks.includes(groceryKey(item))} onchange={()=>shoppingChecks=toggleCheck(shoppingChecks,groceryKey(item))}/><span><strong>{formatIngredient({...item,scale:'fixed'},4,units)}</strong> {item.name}<small>{textInUnits([item.state,item.note,purchaseNote({...item,scale:'fixed'},4)].filter(Boolean).join(' · '))}</small></span></label></li>{/each}</ul></section>{/if}{/each}</div>
      <p class="fine">Amounts are edible ingredient totals, not package counts. Canned legumes are weighed after draining; buy enough cans for that yield. Raw and cooked foods stay separate. Check pantry ingredients before buying. Brand labels govern packaged sauces and bread.</p><button type="button" class="text-button" onclick={()=>{selectedIds=[];shoppingChecks=[];}}>Clear dinner plan</button>
    {/if}
  </section>

  <section class="lesson-section" id="how-to-cook"><p class="eyebrow">MAKE THE METHOD YOURS</p><h2>The low-attention kitchen</h2><p>Every meal uses <strong>Tabular Recipe Notation (TRN)</strong>: ingredient rows feed into merged operation cells from left to right. This recipe-summary format comes from <a href="https://www.cookingforengineers.com/">Michael Chu’s Cooking for Engineers</a>. Read the flow first, then use the detailed method for extra context.</p><p>Small choices do more than an extra appliance. Learn the few rules behind this collection.</p><div class="lesson-grid">
    <details><summary><span>01</span> Active time is the useful clock</summary><p>Count opening cans, cutting, loading, shaking, sauces, shredding, family sides and serving. Passive cooking can overlap prep. “Eight minutes under pressure” is only one stage of dinner.</p></details>
    <details><summary><span>02</span> Give vegetables their own finish line</summary><p>Spread food in one layer. Crowding traps moisture. Start broccoli later, add green beans halfway, and remove fish separately. Two fryers help most when foods need different stop times.</p></details>
    <details><summary><span>03</span> Same main, starch on the side</summary><p>Build one protein-and-vegetable meal. Add ready rice, pita, tortillas or a bun only to family plates. Keep the starch separate in leftovers too. Dry rice cooking is outside these fast timelines.</p></details>
    <details><summary><span>04</span> Make boosters earn their place</summary><p>Ground flax binds turkey. Hemp adds a small nutty finish or enriches eggs. Nutritional yeast finishes vegetables after heat. More seeds do not automatically make a tastier meal.</p></details>
    <details><summary><span>05</span> Scale ingredients, check capacity</summary><p>Twice the food is not the same roast. Keep thickness and spacing fixed; add pans or batches. Pressure liquid follows your model’s minimum, and fill limits still apply. Beat an egg to divide it rather than eyeballing a yolk.</p></details>
    <details><summary><span>06</span> Keep the finish bright</summary><p>Lemon, lime, yogurt and fresh greens balance the cooked food. Pesto goes on the cod after cooking; yeast goes on after roasting. Measured fats and sauces are already included in the nutrition estimate.</p></details>
  </div><div class="evidence-box"><h3>What the numbers mean</h3><p>These recipes were designed for about 25 g or more protein and 100 g or more non-starchy vegetable ingredients per adult. Vegetable weights are before cooking; canned tomato includes juice. Calories and macros use USDA records and specified US labels, including every measured oil, sauce, seed and cheese. Beans, greens, meat fat and draining introduce uncertainty.</p><p>Use Greek yogurt with at least 9 g protein and no more than 4 g total carbs per 100 g. Keep required yogurt and Parmesan portions. Check the pesto and salsa label caps in their recipes. Avoid substituting frozen blocks, raw chicken for cooked chicken, or dry legumes for canned ones.</p><p><a href="https://fdc.nal.usda.gov/">USDA FoodData Central</a> · <a href="https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures">Safe cooking temperatures</a> · <a href="https://instantpot.com/pages/multi-cooker-product-manuals">Your pressure-cooker manual</a></p><h3>Leftovers without extra work</h3><p>Refrigerate in shallow containers within two hours, or one hour above {textInUnits('90°F')}. Use within 3–4 days or freeze; reheat to {textInUnits('165°F')}. Keep cold greens and yogurt separate. <a href="https://ask.fsis.usda.gov/article/How-do-I-handle-leftovers-safely">USDA leftover guidance</a>.</p></div>
  </section>
  <p class="action-status" role="status" aria-live="polite">{message}</p>
  <div class="print-output"><RecipePrint recipes={printRecipes} settings={printSettings} groceries={printGroceries} showShopping={effectivePrintMode==='plan'||effectivePrintMode==='all'} shoppingOnly={effectivePrintMode==='shopping'} chartOnly={effectivePrintMode==='chart'}/></div>
</section>

<style>
  .meal-library{--ink:#25392b;--muted:#53614e;--line:#d4dacb;--paper:#fffef8;--accent:#365b3d;--soft:#e8ecdf;--warm:#f1dfb7;background:#f5f4ec;border-radius:16px;padding:18px;container-type:inline-size;color:var(--ink);font:16px/1.55 system-ui,sans-serif;min-width:0}
  .meal-library :global(*){box-sizing:border-box}.meal-library :global(button),.meal-library :global(input),.meal-library :global(select){font:inherit}.meal-library :global(button),.meal-library :global(select){min-height:44px}.meal-library :global(button){cursor:pointer}.meal-library :global(button:disabled){cursor:default;opacity:.7}.meal-library :global(a){color:var(--accent);text-underline-offset:3px}.meal-library :global(:focus-visible){outline:3px solid #a65c16;outline-offset:3px}.meal-library :global(h2:focus){outline:none}.meal-library :global(h1),.meal-library :global(h2),.meal-library :global(h3){line-height:1.18;letter-spacing:-.035em;color:var(--ink)}.meal-library :global(h2){font-size:clamp(1.6rem,3vw,2.1rem);margin:0 0 .8rem}.meal-library :global(h3){font-size:1.2rem}.meal-library :global(p){margin:.65rem 0 1rem}.meal-library :global(label){font-size:.86rem;font-weight:600}.meal-library :global(input[type=checkbox]){width:19px;height:19px;min-height:19px;accent-color:var(--accent);flex-shrink:0}.meal-library :global(select),.meal-library :global(input[type=search]){background:var(--paper);color:var(--ink);border:1px solid #aeb8a2;border-radius:8px;padding:10px;max-width:100%;min-width:0}.meal-library :global(select){display:block;width:100%}.meal-library :global(summary){cursor:pointer;font-weight:650;min-height:44px;padding:10px 0}.meal-library :global(details p),.meal-library :global(details li){font-size:.95rem}.meal-library :global(details){border-top:1px solid var(--line)}.meal-library :global(small){display:block;font-size:.77rem;font-weight:400;color:var(--muted);line-height:1.45;margin-top:3px}.meal-library :global(ul){padding-left:1.25rem}.meal-library :global(li){margin:.35rem 0}.eyebrow{font-size:.74rem!important;letter-spacing:.13em;font-weight:750;color:var(--muted);margin:0 0 .9rem!important}.library-intro{padding:58px 0 35px;max-width:800px}.library-intro .library-title{font:600 clamp(2.7rem,6vw,4.9rem)/1.03 Georgia,serif;letter-spacing:-.045em;margin:0 0 22px}.lead{font-size:1.13rem;max-width:670px}.intro-facts{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0}.intro-facts span{background:var(--soft);border-radius:100px;padding:7px 13px;font-size:.83rem;font-weight:600}.evidence-note,.fine{font-size:.8rem!important;color:var(--muted);line-height:1.5}.section-top{display:flex;justify-content:space-between;align-items:center;gap:16px}.section-top>a{font-size:.88rem;white-space:nowrap}.filter-box{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:20px}.group-buttons{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px}.group-buttons button{background:transparent;border:1px solid var(--line);border-radius:100px;color:var(--ink);padding:8px 16px}.group-buttons button.chosen{background:var(--accent);border-color:var(--accent);color:#fff}.primary-filters{display:grid;grid-template-columns:1.7fr 1fr 1fr 1fr;gap:12px}.primary-filters label input,.primary-filters label select{margin-top:6px}.search-label input{width:100%}.extra-filters{margin-top:14px}.secondary-filters{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px}.secondary-filters select{margin-top:6px}.secondary-filters fieldset{grid-column:1/-1;border:0;padding:0;margin:0;min-width:0}.secondary-filters legend{font-size:.86rem;font-weight:650}.check-row{display:flex;gap:10px 16px;flex-wrap:wrap;margin-top:6px}.check-row label{display:flex;align-items:center;gap:6px;min-height:32px}.results-toolbar{display:flex;align-items:center;gap:16px;border-top:1px solid var(--line);padding-top:14px}.results-toolbar p{font-size:.86rem;margin:0;margin-right:auto}.results-toolbar label{display:flex;align-items:center;gap:8px}.results-toolbar select{width:auto}.text-button{border:0;background:transparent;color:var(--accent);padding:8px 3px;text-decoration:underline;text-underline-offset:3px;font-size:.85rem!important}.household-settings{padding:18px 0;display:flex;align-items:center;gap:20px}.household-settings>div{margin-right:auto}.household-settings>div>span{display:block;font-size:.78rem;color:var(--muted)}.household-settings label{min-width:105px}.household-settings label>span{font-weight:400;font-size:.75rem}.household-settings select{margin-top:5px}.capacity-alert{font-size:.9rem;background:var(--warm);border-left:3px solid #986425;padding:12px 14px}.recipe-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.recipe-card{background:var(--paper);border:1px solid var(--line);border-radius:16px;display:flex;flex-direction:column;padding:20px;min-width:0}.recipe-card.planned{border-color:#66896b;box-shadow:inset 0 0 0 1px #66896b}.card-top{display:flex;justify-content:space-between;gap:10px;align-items:center}.badge{font-size:.69rem;text-transform:uppercase;letter-spacing:.055em;font-weight:750;border-radius:6px;padding:4px 7px;background:#e3ead8}.badge.shared{background:#ede1c8}.badge.nonketo{background:#e8e3f0}.appliance{font-size:.73rem;color:var(--muted)}.recipe-card h3{margin:18px 0 8px}.title-button{display:block;text-align:left;font:600 1.5rem/1.18 Georgia,serif!important;background:transparent;border:0;padding:0;color:var(--ink);min-height:0!important}.title-button:hover{text-decoration:underline;text-underline-offset:4px}.card-summary{font-size:.87rem;line-height:1.5;color:var(--muted);margin:0 0 18px!important;flex-grow:1}.card-numbers{display:grid;grid-template-columns:1fr 1.55fr 1fr;gap:8px;border-top:1px solid var(--line);padding-top:13px;margin:0}.card-numbers dt{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}.card-numbers dd{font-size:.86rem;font-weight:650;margin:4px 0 0}.attention{font-size:.77rem;color:var(--muted);margin:12px 0!important;min-height:2.4em}.card-actions{display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--line);padding-top:12px;gap:10px}.open-button{border:0;background:transparent;color:var(--accent);padding:0;font-weight:700!important;font-size:.84rem!important}.card-actions label{min-height:44px;font-size:.77rem;display:flex;gap:6px;align-items:center}.plan-bar{background:var(--accent);color:#fff;padding:15px 18px;border-radius:10px;margin-top:18px;display:flex;justify-content:space-between;gap:16px;font-size:.88rem}.plan-bar a{color:#fff!important}.empty{text-align:center;padding:35px;background:var(--soft);border-radius:12px}.empty button,.detail-bottom>button:first-child{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:10px 15px}.recipe-detail{margin-top:50px;padding:28px;background:var(--paper);border:1px solid var(--line);border-radius:20px;scroll-margin-top:20px}.detail-toolbar{display:flex;justify-content:space-between;gap:14px;margin-bottom:24px}.detail-toolbar>div{display:flex;gap:8px;flex-wrap:wrap}.outline{border:1px solid #b7c1aa;background:transparent;color:var(--ink);border-radius:8px;padding:8px 12px;font-size:.8rem!important}.recipe-detail h2{font:600 clamp(2rem,4vw,3rem)/1.13 Georgia,serif;max-width:800px}.detail-summary{max-width:700px;color:var(--muted)}.detail-facts{display:flex;gap:25px;flex-wrap:wrap;margin:20px 0}.detail-facts span{font-size:.84rem}.detail-facts strong{display:block;font-size:1.1rem;color:var(--ink)}.family-box{background:#f1ecd9;border-radius:12px;padding:16px 20px;margin:20px 0}.family-box h3{margin:0}.family-box p{font-size:.9rem}.family-box select{max-width:360px;margin-top:6px}.detail-columns{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.55fr);gap:35px;margin-top:26px}.ingredients,.groceries{list-style:none;padding:0!important}.ingredients li,.groceries li{border-bottom:1px solid var(--line);padding:8px 0;margin:0!important}.ingredients label,.groceries label{display:flex;align-items:flex-start;gap:10px;line-height:1.5;font-size:.88rem;font-weight:400}.checked>label>span{opacity:.65;text-decoration:line-through}.checked>label>span small{text-decoration:none}.family-ingredient{padding:12px 0;border-bottom:1px solid var(--line);font-size:.88rem}.family-ingredient p{margin:.4rem 0}.nutrition{margin-top:20px}.nutrition dl{display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.84rem}.nutrition dl>div{padding:8px;background:var(--soft);border-radius:6px}.nutrition dt{font-size:.73rem;color:var(--muted)}.nutrition dd{font-weight:650;margin:2px 0}.family-macros{font-size:.84rem;background:#f1ecd9;padding:10px;border-radius:6px}.equipment{font-size:.9rem}.safe-note{font-size:.8rem;color:var(--muted);border-left:2px solid #b4bea5;padding-left:12px}.steps{list-style:none;counter-reset:step;padding:0}.steps li{counter-increment:step;border-bottom:1px solid var(--line);padding:15px 0;margin:0!important}.steps li::before{content:counter(step,decimal-leading-zero);color:#77916b;font:500 1.2rem Georgia,serif;float:left;margin-right:10px}.steps label{display:flex;align-items:flex-start;gap:8px;font-size:.95rem;font-weight:400}.steps label>span>strong{display:block;font-size:1rem;margin-bottom:5px}.steps label>span>span{display:block;line-height:1.65}.timeline{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.timeline>div{background:var(--soft);border-radius:8px;padding:12px;min-width:0}.timeline strong{font-size:.83rem;display:block}.timeline span{font-size:.75rem;color:var(--muted)}.timeline p{font-size:.78rem;line-height:1.5;margin:.5rem 0 0}.detail-bottom{display:flex;gap:18px;margin-top:22px;align-items:center}.shopping-section,.lesson-section{margin-top:50px;border-top:1px solid var(--line);padding-top:30px;scroll-margin-top:20px}.shopping-section>p,.lesson-section>p{max-width:750px}.planned-meals{list-style:none;padding:0!important}.planned-meals li{display:flex;align-items:center;gap:15px;border-bottom:1px solid var(--line);padding:10px 0;font-size:.9rem}.planned-meals li>span{flex:1}.planned-meals select{font-size:.78rem}.grocery-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:25px}.grocery-grid>section{padding:18px;background:var(--paper);border-radius:12px;border:1px solid var(--line)}.grocery-grid h3{margin:0 0 10px}.lesson-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:22px 0}.lesson-grid details{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 18px}.lesson-grid summary{font-size:.92rem}.lesson-grid summary span{color:#77916b;margin-right:8px;font-family:Georgia,serif}.evidence-box{padding:22px;background:var(--soft);border-radius:12px;font-size:.9rem}.evidence-box h3{margin:0 0 12px}.evidence-box h3:not(:first-child){margin-top:22px}.action-status{font-size:.85rem;color:var(--accent)}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}.cookingFocus .library-intro,.cookingFocus .browse,.cookingFocus .shopping-section,.cookingFocus .lesson-section{display:none}.cookingFocus .recipe-detail{margin-top:24px}.cookingFocus .recipe-detail .ingredient-panel{position:sticky;top:15px;align-self:start}
  @container(max-width:1000px){.recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.primary-filters{grid-template-columns:1fr 1fr}.detail-columns{grid-template-columns:1fr 1.2fr;gap:22px}.household-settings>div{max-width:170px}.timeline{grid-template-columns:1fr}}
  @container(max-width:600px){.recipe-grid,.detail-columns,.grocery-grid,.lesson-grid{grid-template-columns:1fr}.primary-filters{grid-template-columns:1fr 1fr}.search-label{grid-column:1/-1}.primary-filters label:last-child{grid-column:1/-1}.household-settings{display:grid;grid-template-columns:1fr 1fr}.household-settings>div,.household-settings>label:last-child{grid-column:1/-1}.detail-toolbar{flex-direction:column}.plan-bar{flex-direction:column}.section-top{align-items:flex-start;flex-direction:column}.planned-meals li{flex-wrap:wrap}.secondary-filters{grid-template-columns:1fr}.secondary-filters fieldset{grid-column:auto}}
  @media(max-width:1000px){.recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.primary-filters{grid-template-columns:1fr 1fr}.secondary-filters{grid-template-columns:1fr 1fr}.secondary-filters fieldset{grid-column:1/-1}.detail-columns{gap:25px;grid-template-columns:1fr 1.2fr}.household-settings{gap:12px}.timeline{grid-template-columns:1fr}.household-settings>div{max-width:170px}}
  @media(max-width:600px){.meal-library{padding:12px}.library-intro{padding:35px 0 24px}.library-intro .library-title{font-size:3rem}.lead{font-size:1rem}.section-top{align-items:flex-start;flex-direction:column;gap:0}.section-top>a{margin-bottom:12px}.filter-box{padding:14px;border-radius:12px}.group-buttons{gap:5px}.group-buttons button{font-size:.82rem;padding:7px 11px}.primary-filters{gap:10px}.primary-filters label{font-size:.76rem}.search-label{grid-column:1/-1}.primary-filters label:last-child{grid-column:1/-1}.primary-filters select{font-size:.84rem}.results-toolbar{flex-wrap:wrap;gap:8px}.results-toolbar p{width:100%}.results-toolbar label{flex:1}.results-toolbar select{flex:1}.household-settings{display:grid;grid-template-columns:1fr 1fr;padding:17px 0}.household-settings>div{grid-column:1/-1;max-width:none}.household-settings>label:last-child{grid-column:1/-1}.recipe-grid{grid-template-columns:1fr;gap:14px}.recipe-card{padding:18px}.recipe-card h3{margin-top:15px}.card-summary{margin-bottom:14px!important}.attention{min-height:0}.secondary-filters{grid-template-columns:1fr}.secondary-filters fieldset{grid-column:auto}.plan-bar{flex-direction:column;gap:5px}.recipe-detail{padding:18px;margin-top:30px;border-radius:14px}.detail-toolbar{flex-direction:column;margin-bottom:18px;gap:5px}.detail-toolbar>div{gap:6px}.detail-toolbar .outline{padding:7px 9px}.detail-facts{gap:16px}.detail-facts strong{font-size:.95rem}.detail-columns{grid-template-columns:1fr;gap:20px}.timeline{grid-template-columns:1fr}.nutrition dl{grid-template-columns:1fr 1fr}.family-box{padding:15px}.detail-bottom{flex-direction:column;align-items:flex-start;gap:4px}.grocery-grid,.lesson-grid{grid-template-columns:1fr}.planned-meals li{flex-wrap:wrap;gap:8px}.planned-meals li>span{flex-basis:100%}.planned-meals label{flex:1}.shopping-section,.lesson-section{margin-top:32px}.shopping-section .section-top{gap:8px}.cookingFocus .recipe-detail .ingredient-panel{position:static}}
  @media(prefers-reduced-motion:reduce){.meal-library :global(*){scroll-behavior:auto!important}}
  .assistant-copy{display:block;margin:20px 0}.assistant-copy textarea{display:block;width:100%;margin-top:8px;min-height:200px;font:14px/1.5 monospace}.assistant-downloads{margin-top:16px;font-size:14px;line-height:1.6}.print-output{display:none}.print-plan-actions{display:flex;flex-wrap:wrap;gap:8px}
  @media print{
    @page{size:auto;margin:15mm}
    .meal-library{display:block!important;container-type:normal;padding:0!important;margin:0!important;border:0!important;border-radius:0!important;background:white!important;color:black!important}
    .meal-library>:not(.print-output){display:none!important}
    .meal-library>.print-output{display:block!important}
    :global(html[data-recipe-print] .site-header),:global(html[data-recipe-print] .sidebar),:global(html[data-recipe-print] .site-footer),:global(html[data-recipe-print] .breadcrumbs),:global(html[data-recipe-print] .post-meta),:global(html[data-recipe-print] .article-actions),:global(html[data-recipe-print] .related-posts),:global(html[data-recipe-print] .about-card),:global(html[data-recipe-print] .heading-link),:global(html[data-recipe-print] h1:not(.print-title)){display:none!important}
    :global(html[data-recipe-print] .page-layout){display:block!important;max-width:none!important;padding:0!important;margin:0!important}
    :global(html[data-recipe-print]),:global(html[data-recipe-print] body){background:white!important;color:black!important}
  }

  .card-photo{margin:14px 0 0}.card-photo img,.recipe-photo img{display:block;width:100%;height:auto;border-radius:10px}.card-photo figcaption,.recipe-photo figcaption{font-size:.72rem;color:var(--muted);line-height:1.4;margin-top:6px}.recipe-photo{max-width:60rem;margin:22px 0}.image-disclosure{max-width:46rem}.cookingFocus .recipe-photo{display:none}
  @media print{.card-photo,.recipe-photo,.image-disclosure{display:none!important}}
</style>
