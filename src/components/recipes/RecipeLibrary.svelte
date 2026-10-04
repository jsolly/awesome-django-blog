<script>
  import { onMount, tick } from 'svelte';
  import Button from '$lib/components/ui/button/button.svelte';
  import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
  import NativeSelect from '$lib/components/ui/native-select/native-select.svelte';
  import DialogRoot from '$lib/components/ui/dialog/dialog.svelte';
  import DialogContent from '$lib/components/ui/dialog/dialog-content.svelte';
  import DialogTitle from '$lib/components/ui/dialog/dialog-title.svelte';
  import DialogDescription from '$lib/components/ui/dialog/dialog-description.svelte';
  import FilterMultiSelect from './FilterMultiSelect.svelte';
  import NutrientDisclosure from './NutrientDisclosure.svelte';
  import RecipePrint from './RecipePrint.svelte';
  import ApplianceIcon from './ApplianceIcon.svelte';
  import RecipeFlow from './RecipeFlow.svelte';
  import {matchesRecipe,starchTypes,normalizeSelection,normalizeMealStyles,toggleMealStyle,applianceChoices,availableAppliances,defaultAppliances} from './nutrient-filters.mjs';
  import {dailyNutrition} from './nutrition.mjs';
  import { shuffleRecipes, formatIngredient, ingredientAmount, validateSettings, servingNutrition } from './recipe-logic.mjs';
  let { recipes } = $props();
  const groups = { keto: 'Keto', shared: 'Shared main', nonketo: 'Not Keto' };
  let servings = $state(4);
  const units = 'us';
  const familyDiners = $derived(servings);
  let familyChoice = $state({});
  let recipeId = $state('');
  let hydrated = $state(false);
  let printMode = $state('auto');
  let printPrepared = $state(false);
  let previousPrintAttribute = null;
  let ownsPrintAttribute = false;
  let libraryElement=$state(null);
  let message = $state('');
  let detailHeading=$state(null);
  let recipeDialog=$state(null);
  let lastOpenedId="";
  let listHeading=$state(null);
  let results = $state([]);
  let immuneSupport = $state(false);
  let ironRich = $state(false);
  const proteins={chicken:'Chicken',fish:'Fish',turkey:'Turkey',vegetarian:'Vegetarian','plant-forward':'Plant-forward'};
  const carbStyles={keto:'Keto',nonketo:'Not Keto',shared:'Shared Main'};
  let proteinChoice=$state([]);
  let carbChoice=$state([]);
  let starchChoice=$state([]);
  let appliancesOnHand=$state({...defaultAppliances});
  const filterSettings=$derived({protein:proteinChoice,carb:carbChoice,starch:starchChoice,immune:immuneSupport,iron:ironRich,appliances:appliancesOnHand});
  let collection=$state('meal');
  const collectionRecipes=$derived(recipes.filter(recipe=>(recipe.type||'meal')===collection));
  const eligibleRecipes = $derived(collectionRecipes.filter(recipe=>matchesRecipe(recipe,servings,filterSettings)));
  function hasMatches(overrides){return collectionRecipes.some(recipe=>matchesRecipe(recipe,servings,{...filterSettings,...overrides}));}
  const visibleRecipes = $derived(results.filter(recipe => eligibleRecipes.includes(recipe)));
  const current = $derived(recipes.find(r => r.id === recipeId));
  const printSettings = $derived({servings,units,familyDiners,familyChoice});
  const effectivePrintMode = $derived(printMode==='auto' ? (current ? 'recipe' : 'all') : printMode);
  const printRecipes = $derived(effectivePrintMode==='recipe'&&current ? [current] : collectionRecipes);
  const baseNutrition = $derived(current ? servingNutrition(current,servings) : null);
  const dailyValues = $derived(current ? dailyNutrition(current,servings,ingredientAmount).filter(n=>n.amount!==null) : []);
  function setCollection(value){
    collection=value;
    if(!recipes.some(recipe=>(recipe.type||'meal')===value&&matchesRecipe(recipe,servings,{...filterSettings,appliances:defaultAppliances}))){proteinChoice=[];starchChoice=[];carbChoice=[];immuneSupport=false;ironRich=false;}
  }
  const storageKey = 'blogthedata-recipes-v2';

  function choiceFor(recipe) { return recipe.familyOptions?.find(o=>o.id===familyChoice[recipe.id])?.id || recipe.familyOptions?.[0]?.id || ''; }
  function setServings(value) { const valid = validateSettings({servings:Number(value),familyDiners,units}); servings=valid.servings; }
  function setChoice(id,value) { familyChoice={...familyChoice,[id]:value}; }
  async function openRecipe(id,scroll=true) {
    recipeId=id;setCollection(recipes.find(recipe=>recipe.id===id)?.type||'meal');lastOpenedId=id;message='';
    if(window.location.hash!==`#${id}`)history.pushState(null,'',`#${id}`);
    await tick();

    if(scroll && detailHeading) {detailHeading.focus({preventScroll:true});recipeDialog.scrollTop=0;}
  }
  async function backToResults(updateURL=true) {
    recipeId='';
    if(updateURL)history.pushState(null,'','#meal-results');
    await tick();
    const trigger=libraryElement?.querySelector(`[data-recipe-id="${lastOpenedId}"]`);
    (trigger||listHeading)?.focus({preventScroll:true});
    if(trigger)trigger.scrollIntoView({block:'center'});else listHeading?.scrollIntoView({block:'start'});
  }
  function readURL() {
    const p = new URLSearchParams(window.location.search);
    const settings=validateSettings({servings:p.get('servings')===null?servings:Number(p.get('servings'))});
    servings=settings.servings;
    const choices={};for(const part of (p.get('starch')||'').split(',')){const [rid,oid]=part.split(':');if(recipes.find(r=>r.id===rid)?.familyOptions.some(o=>o.id===oid))choices[rid]=oid;}familyChoice={...familyChoice,...choices};
    const id=window.location.hash.slice(1);
    if(recipes.some(r=>r.id===id))recipeId=id;
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
  onMount(()=>{
    try { const saved=JSON.parse(localStorage.getItem(storageKey)||'null'); if(saved && typeof saved==='object') {const s=validateSettings(saved);servings=s.servings;collection=saved.collection==='smoothie'?'smoothie':'meal';proteinChoice=normalizeSelection(saved.proteinChoice,proteins);carbChoice=normalizeMealStyles(saved.carbChoice);appliancesOnHand=availableAppliances(saved.appliancesOnHand);starchChoice=normalizeSelection(saved.starchChoice,starchTypes);immuneSupport=saved.immuneSupport===true;ironRich=saved.ironRich===true;familyChoice=saved.familyChoice&&typeof saved.familyChoice==='object'?saved.familyChoice:{};} } catch {/* Reading remains usable without storage. */}
    readURL();setCollection(collection);results=shuffleRecipes(recipes);hydrated=true;if(recipeId)void openRecipe(recipeId);
    window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',restorePrint);
    const hash=()=>{const id=window.location.hash.slice(1);if(recipes.some(r=>r.id===id))void openRecipe(id,true);else if(recipeId)void backToResults(false);};window.addEventListener('hashchange',hash);
    return()=>{window.removeEventListener('hashchange',hash);window.removeEventListener('beforeprint',preparePrint);window.removeEventListener('afterprint',restorePrint);restorePrint();};
  });
  $effect(()=>{if(hydrated){try{localStorage.setItem(storageKey,JSON.stringify({servings,familyDiners,units,familyChoice,immuneSupport,ironRich,proteinChoice,carbChoice,starchChoice,appliancesOnHand,collection}));}catch {/* No persistence required to cook. */}}});
</script>

<section class="meal-library" data-hydrated={hydrated} data-print-prepared={printPrepared} bind:this={libraryElement} aria-label="Easy Meals recipe library">
  <div class="library-controls" aria-label="Recipe options"><div class="collection-options" aria-label="Recipe type"><Button variant="ghost" type="button" aria-pressed={collection==='meal'} onclick={()=>setCollection('meal')}>Meals</Button><Button variant="ghost" type="button" aria-pressed={collection==='smoothie'} onclick={()=>setCollection('smoothie')}>Smoothies</Button></div><div class="library-intro">
    <label class="servings-setting">Servings<NativeSelect aria-label="Servings" value={servings} onchange={e=>setServings(e.currentTarget.value)} disabled={!hydrated}>{#each [2,4,6,8] as n (n)}<option value={n}>{n}</option>{/each}</NativeSelect></label>

  </div>

  <div class="recipe-filter-selects"><FilterMultiSelect label="Protein" options={proteins} bind:selected={proteinChoice} emptyLabel="All proteins" disabled={!hydrated} canSelect={values=>hasMatches({protein:values})}/><FilterMultiSelect label="Carb" options={Object.fromEntries(Object.entries(starchTypes).filter(([key])=>key!=='all'))} bind:selected={starchChoice} emptyLabel="All starches" disabled={!hydrated} canSelect={values=>hasMatches({starch:values})}/><fieldset class="carb-types"><legend>Meal style</legend><div class="carb-type-options">{#each Object.entries(carbStyles) as [value,label] (value)}<Button variant="ghost" type="button" aria-pressed={carbChoice.includes(value)} disabled={!hydrated||!hasMatches({carb:toggleMealStyle(carbChoice,value)})} onclick={()=>carbChoice=toggleMealStyle(carbChoice,value)}>{label}</Button>{/each}</div></fieldset></div>
  <fieldset class="inventory"><legend>Appliances on hand</legend>{#each Object.entries(applianceChoices) as [value,label] (value)}{#if ['Instant Pot','Two air fryers'].includes(value)}<label class="inventory-count"><ApplianceIcon name={value} decorative/>{label}<NativeSelect aria-label={`${label} count`} disabled={!hydrated} value={appliancesOnHand[value]} onchange={event=>appliancesOnHand={...appliancesOnHand,[value]:Number(event.currentTarget.value)}}>{#each [0,1,2] as count (count)}<option value={count}>{count}</option>{/each}</NativeSelect></label>{:else}<label class:unavailable={value==='Pans'&&!appliancesOnHand.Oven}><Checkbox checked={appliancesOnHand[value]>0} onCheckedChange={()=>appliancesOnHand={...appliancesOnHand,[value]:appliancesOnHand[value]?0:1}} disabled={!hydrated||(value==='Pans'&&!appliancesOnHand.Oven)}/><ApplianceIcon name={value} decorative/>{label}</label>{/if}{/each}</fieldset>
  <fieldset class="nutrient-filters"><legend>Nutrition<Button variant="ghost" type="button" class="filter-info" popovertarget="nutrition-filter-info" aria-label="About nutrition filters"><span aria-hidden="true">ⓘ</span></Button></legend><label title="At least 20% Daily Value in two or more of vitamins A, C, D, zinc and selenium per serving"><Checkbox bind:checked={immuneSupport} disabled={!hydrated||(!immuneSupport&&!hasMatches({immune:true}))}/> Immune support</label><label title="At least 20% Daily Value of iron per serving"><Checkbox bind:checked={ironRich} disabled={!hydrated||(!ironRich&&!hasMatches({iron:true}))}/> Iron-rich</label></fieldset><Button variant="ghost" type="button" class="outline print-all" disabled={!hydrated} onclick={()=>print('all')}>{collection==='smoothie'?'Print smoothies':'Print meals'}</Button></div>

  <div id="nutrition-filter-info" popover="auto" class="filter-popover" aria-labelledby="nutrition-filter-info-title"><h3 id="nutrition-filter-info-title">Nutrition filters</h3><p><strong>Iron-rich:</strong> at least 20% Daily Value of iron per serving.</p><p><strong>Immune support:</strong> at least 20% Daily Value in two or more of vitamins A, C, D, zinc and selenium per serving.</p><Button variant="ghost" type="button" class="outline" popovertarget="nutrition-filter-info" popovertargetaction="hide">Close</Button></div>

  <div class="browse" id="meal-results">
    <h2 bind:this={listHeading} tabindex="-1">{collection==='smoothie'?'Find your smoothie':'Find your meal'}</h2>
    <div class="recipe-grid">
      {#each visibleRecipes as recipe (recipe.id)}
        <article class="recipe-card">
          <div class="card-top"><span class="badge" class:shared={recipe.group==='shared'} class:nonketo={recipe.group==='nonketo'}>{groups[recipe.group]}</span></div>
          {#if recipe.image}<figure class="card-photo"><img src={recipe.image.cardSrc} srcset={recipe.image.cardSrcset} sizes="(max-width:600px) 340px, (max-width:1000px) 420px, 360px" width={recipe.image.width} height={recipe.image.height} alt={recipe.image.alt} loading="lazy" decoding="async"/></figure>{/if}
          <h3><Button variant="ghost" type="button" class="title-button" data-recipe-id={recipe.id} disabled={!hydrated} onclick={()=>openRecipe(recipe.id)}>{recipe.title}</Button></h3>
          <dl class="card-numbers"><div><dt>Active time</dt><dd>{recipe.activeMinutes}{servings>4?'+':''} min</dd></div><div><dt>Net carbs per {servings} servings</dt><dd>{Math.round(servingNutrition(recipe,servings).net_carbs_g * servings)} g</dd></div><div><dt>Appliances needed</dt><dd class="appliance-icons">{#each recipe.appliancesNeeded as name (name)}<ApplianceIcon {name}/>{/each}</dd></div></dl>
          <div class="card-actions"><Button variant="ghost" class="open-button" type="button" disabled={!hydrated} onclick={()=>openRecipe(recipe.id)}>See recipe <span aria-hidden="true">↗</span></Button></div>
        </article>
      {/each}
    </div>
    {#if hydrated && !visibleRecipes.length}<p>No recipes match these appliances and filters.</p>{/if}
  </div>

  {#if current}
    <DialogRoot open={Boolean(current)} onOpenChange={open=>{if(!open)void backToResults();}}><DialogContent class="recipe-takeover translate-x-0 translate-y-0 top-0 left-0 data-open:animate-none data-closed:animate-none" bind:ref={recipeDialog} showCloseButton={false} onOpenAutoFocus={event=>{event.preventDefault();detailHeading?.focus({preventScroll:true});}} onCloseAutoFocus={event=>event.preventDefault()}><section class="recipe-detail" id={current.id} aria-labelledby="recipe-detail-title">
      <div class="detail-toolbar"><Button variant="ghost" type="button" class="text-button" onclick={()=>backToResults()}>← Back to recipes</Button><Button variant="ghost" type="button" class="outline" onclick={()=>print('recipe')}>Print recipe</Button></div>
      <span class="badge" class:shared={current.group==='shared'} class:nonketo={current.group==='nonketo'}>{groups[current.group]}</span>
      <DialogTitle id="recipe-detail-title" tabindex="-1" bind:ref={detailHeading}>{current.title}</DialogTitle>
      <DialogDescription class="detail-summary">{current.summary}</DialogDescription>
      <div class="detail-appliances"><span>Appliances needed</span><div class="appliance-icons">{#each current.appliancesNeeded as name (name)}<ApplianceIcon {name}/>{/each}</div></div>
      <div class="detail-facts"><span><strong>{current.activeMinutes}{servings>4?'+':''} min</strong> active time{servings>4?' / base batch':''}</span><span><strong>{servings}</strong> servings</span></div>
      {#if current.image}<figure class="recipe-photo"><img src={current.image.src} srcset={current.image.detailSrcset} sizes="(max-width:600px) 320px, (max-width:1000px) 680px, 960px" width={current.image.width} height={current.image.height} alt={current.image.alt} loading="eager" decoding="async"/></figure>{/if}
        {#if current.familyOptions.length}
        {@const option=current.familyOptions.find(o=>o.id===choiceFor(current))||current.familyOptions[0]}
        <div class="family-box"><label>Family side<NativeSelect aria-label="Family starch" value={choiceFor(current)} onchange={e=>setChoice(current.id,e.currentTarget.value)}>{#each current.familyOptions as option (option.id)}<option value={option.id}>{option.label}</option>{/each}</NativeSelect></label><p>{formatIngredient({...option,amount:option.amount*familyDiners,us:option.us?{...option.us,amount:option.us.amount*familyDiners}:undefined,scale:'fixed'},4,units)} {option.ingredientName} · serve separately</p></div>
      {/if}
      {#key current.id}<RecipeFlow recipe={current} settings={printSettings}/>{/key}
      <section class="nutrition" aria-label="Nutrition per serving"><h3>Nutrition per serving</h3><dl><div><dt>Calories</dt><dd>{Math.round(baseNutrition.kcal)} kcal</dd></div><div><dt>Protein</dt><dd>{Math.round(baseNutrition.protein_g)} g</dd></div><div><dt>Total carbs</dt><dd>{Math.round(baseNutrition.carbs_g)} g</dd></div><div><dt>Fiber</dt><dd>{Math.round(baseNutrition.fiber_g)} g</dd></div><div><dt>Net carbs</dt><dd>{Math.round(baseNutrition.net_carbs_g)} g</dd></div></dl>{#key current.id}<NutrientDisclosure nutrients={dailyValues}/>{/key}</section>

    </section></DialogContent></DialogRoot>
  {/if}

  <p class="action-status" role="status" aria-live="polite">{message}</p>
  <div class="print-output"><RecipePrint recipes={printRecipes} settings={printSettings}/></div>
</section>

<style>
  .meal-library{--ink:#25392b;--muted:#53614e;--line:#d4dacb;--paper:#fffef8;--accent:#365b3d;--soft:#e8ecdf;--warm:#f1dfb7;background:#f5f4ec;border-radius:16px;padding:18px;container-type:inline-size;color:var(--ink);font:16px/1.55 var(--font-body);min-width:0}
  .meal-library :global(*){box-sizing:border-box}.meal-library :global(button),.meal-library :global(input),.meal-library :global(select){font:inherit}.meal-library :global(button),.meal-library :global(select){min-height:44px}.meal-library :global(button){cursor:pointer}.meal-library :global(button:disabled){cursor:default;opacity:.7}.meal-library :global(a){color:var(--accent);text-underline-offset:3px}.meal-library :global(:focus-visible){outline:3px solid #a65c16;outline-offset:3px}.meal-library :global(h2:focus){outline:none}.meal-library :global(h1),.meal-library :global(h2),.meal-library :global(h3){line-height:1.18;letter-spacing:-.035em;color:var(--ink)}.meal-library :global(h2){font-size:clamp(1.6rem,3vw,2.1rem);margin:0 0 .8rem}.meal-library :global(h3){font-size:1.2rem}.meal-library :global(p){margin:.65rem 0 1rem}.meal-library :global(label){font-size:.86rem;font-weight:600}.meal-library :global(input[type=checkbox]){width:19px;height:19px;min-height:19px;accent-color:var(--accent);flex-shrink:0}.meal-library :global(select),.meal-library :global(input[type=search]){background:var(--paper);color:var(--ink);border:1px solid #aeb8a2;border-radius:8px;padding:10px;max-width:100%;min-width:0}.meal-library :global(select){display:block;width:100%}.meal-library :global(summary){cursor:pointer;font-weight:650;min-height:44px;padding:10px 0}.meal-library :global(details p),.meal-library :global(details li){font-size:.95rem}.meal-library :global(details){border-top:1px solid var(--line)}.meal-library :global(small){display:block;font-size:.77rem;font-weight:400;color:var(--muted);line-height:1.45;margin-top:3px}.meal-library :global(ul){padding-left:1.25rem}.meal-library :global(li){margin:.35rem 0}.recipe-filter-selects{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:16px}.carb-types{grid-column:1/-1;border:0;padding:0;margin:0;min-width:0}.carb-types legend{font-size:.86rem;font-weight:600;margin-bottom:6px;padding:0}.carb-type-options{display:flex;gap:6px;flex-wrap:wrap}.carb-type-options :global(button){border:1px solid #aeb8a2;border-radius:8px;background:var(--paper);color:var(--ink);padding:8px 12px;font-size:.8rem!important;font-weight:600}.carb-type-options :global(button[aria-pressed=true]){background:var(--accent);border-color:var(--accent);color:white}.library-controls{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:24px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px 24px}.collection-options{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:6px;background:var(--soft);border-radius:14px}.collection-options :global(button){min-height:72px!important;background:transparent;color:var(--ink);border:1px solid transparent;border-radius:10px;padding:16px;font:600 clamp(1.1rem,3vw,1.4rem)/1.2 var(--font-heading)!important}.collection-options :global(button[aria-pressed=true]){background:var(--accent);color:white}.inventory-count :global(select){width:65px!important;display:inline-block!important}.inventory .unavailable{opacity:.45}.inventory{grid-column:1/-1;border:0;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:8px 16px}.inventory legend{font-size:.8rem;font-weight:650;margin-bottom:8px;padding:0}.inventory label{display:flex;align-items:center;gap:8px;min-height:44px}.nutrient-filters{border:0;padding:0;margin:0;display:flex;align-items:center;gap:8px 20px;flex-wrap:wrap;grid-column:1;grid-row:5}.nutrient-filters legend{display:flex;width:auto;align-items:center;font-size:.8rem;font-weight:650;margin-bottom:0;padding:0}.nutrient-filters label{display:flex;align-items:center;gap:8px;min-height:44px}:global(.filter-info){margin-left:4px;border:0;background:none;color:var(--accent);width:28px;padding:0;font-size:1.05rem!important}.filter-popover{max-width:380px;width:calc(100% - 32px);border:1px solid var(--line);border-radius:12px;padding:20px;background:var(--paper);color:var(--ink);box-shadow:0 8px 30px #0002}.filter-popover h3{margin-top:0}.filter-popover::backdrop{background:transparent}.library-intro{display:grid;grid-template-columns:auto;align-items:center;gap:24px;grid-column:1/-1}:global(.print-all){align-self:end;justify-self:end;grid-column:2;grid-row:5}.library-intro>.servings-setting{grid-column:1;grid-row:1}.servings-setting{display:flex;align-items:center;gap:10px}.servings-setting :global(select){width:auto}:global(.text-button){border:0;background:transparent;color:var(--accent);padding:8px 3px;text-decoration:underline;text-underline-offset:3px;font-size:.85rem!important}.recipe-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.recipe-card{background:var(--paper);border:1px solid var(--line);border-radius:16px;display:grid;grid-template-rows:subgrid;grid-row:span 5;padding:20px;min-width:0;row-gap:0}.card-top{display:flex;justify-content:space-between;gap:10px;align-items:center}.badge{font-size:.69rem;text-transform:uppercase;letter-spacing:.055em;font-weight:750;border-radius:6px;padding:4px 7px;background:#e3ead8}.badge.shared{background:#ede1c8}.badge.nonketo{background:#e8e3f0}.recipe-card h3{margin:18px 0 8px}:global(.title-button){display:block;text-align:left;white-space:normal;font:600 1.5rem/1.18 var(--font-heading)!important;background:transparent;border:0;padding:0;color:var(--ink);min-height:0!important}:global(.title-button):hover{text-decoration:underline;text-underline-offset:4px}.card-numbers{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;border-top:1px solid var(--line);padding-top:13px;margin:12px 0 0}.card-numbers>div{display:grid;grid-template-rows:1fr auto}.card-numbers>div:last-child{grid-column:1/-1}.card-numbers dt{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}.card-numbers dd{font-size:.86rem;font-weight:650;margin:4px 0 0}.appliance-icons{display:flex;align-items:center;gap:10px}.card-actions{margin-top:16px}.card-actions{display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--line);padding-top:12px;gap:10px}:global(.open-button){border:0;background:transparent;color:var(--accent);padding:0;font-weight:700!important;font-size:.84rem!important}:global(.recipe-takeover){--ink:#25392b;--muted:#53614e;--line:#d4dacb;--paper:#fffef8;--accent:#365b3d;--soft:#e8ecdf;font:16px/1.55 var(--font-body);position:fixed;inset:0;transform:none;translate:none;display:block;box-shadow:none;border-radius:0;width:100%;height:100dvh;max-width:none;max-height:none;margin:0;border:0;padding:24px;background:#f5f4ec;color:var(--ink);overflow:auto;overscroll-behavior:contain}:global(.recipe-takeover)::backdrop{background:#f5f4ec}.recipe-detail{max-width:1100px;margin:0 auto!important;padding:28px;background:var(--paper);border:1px solid var(--line);border-radius:20px;scroll-margin-top:20px}.detail-toolbar{display:flex;justify-content:space-between;gap:14px;margin-bottom:24px}:global(.outline){border:1px solid #b7c1aa;background:transparent;color:var(--ink);border-radius:8px;padding:8px 12px;font-size:.8rem!important}.recipe-detail>.badge{display:inline-block;margin-bottom:12px}.recipe-detail :global(h2){font:600 clamp(2rem,4vw,3rem)/1.13 var(--font-heading);max-width:800px}:global(.detail-summary){max-width:700px;color:var(--muted)}.detail-appliances{display:flex;align-items:center;gap:14px;margin:16px 0;font-size:.84rem}.detail-facts{display:flex;gap:25px;flex-wrap:wrap;margin:20px 0}.detail-facts span{font-size:.84rem}.detail-facts strong{display:block;font-size:1.1rem;color:var(--ink)}.family-box{background:#f1ecd9;border-radius:12px;padding:16px 20px;margin:20px 0}.family-box p{font-size:.9rem}.family-box :global(select){max-width:360px;margin-top:6px}.family-box :global(select),.servings-setting :global(select){appearance:none;padding-right:40px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath d='m4 6 4 4 4-4' fill='none' stroke='%2325392b' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 14px center}.nutrition{margin-top:20px}.nutrition dl{display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.84rem}.nutrition dl>div{padding:8px;background:var(--soft);border-radius:6px}.nutrition dt{font-size:.73rem;color:var(--muted)}.nutrition dd{font-weight:650;margin:2px 0}.action-status{font-size:.85rem;color:var(--accent)}
  @container(max-width:1000px){.recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  @container(max-width:600px){.recipe-grid{grid-template-columns:1fr}}
  @media(max-width:1000px){.recipe-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  @media(max-width:600px){.meal-library{padding:12px}.library-controls{padding:14px;gap:12px}.library-intro{grid-template-columns:1fr;gap:14px}.recipe-filter-selects{grid-template-columns:1fr}:global(.print-all){grid-column:1/-1;grid-row:6;justify-self:end}.library-intro>.servings-setting{grid-column:1;grid-row:1}.nutrient-filters{gap:4px 12px;grid-column:1/-1}.recipe-grid{grid-template-columns:1fr;gap:14px}.recipe-card{padding:18px}.recipe-card h3{margin-top:15px}:global(.recipe-takeover){padding:12px}.recipe-detail{padding:18px;border-radius:14px}.detail-toolbar{flex-direction:column;margin-bottom:18px;gap:5px}.detail-toolbar :global(.outline){padding:7px 9px}.detail-facts{gap:16px}.detail-facts strong{font-size:.95rem}.nutrition dl{grid-template-columns:1fr 1fr}.family-box{padding:15px}}
  @media(prefers-reduced-motion:reduce){.meal-library :global(*){scroll-behavior:auto!important}}
  .print-output{display:none}
  @media print{
    @page{size:auto;margin:15mm}
    .meal-library{display:block!important;container-type:normal;padding:0!important;margin:0!important;border:0!important;border-radius:0!important;background:white!important;color:black!important}
    .meal-library>:not(.print-output){display:none!important}:global(.recipe-takeover),:global([data-slot=dialog-overlay]){display:none!important}
    .meal-library>.print-output{display:block!important}
    :global(html[data-recipe-print] .site-header),:global(html[data-recipe-print] .sidebar),:global(html[data-recipe-print] .site-footer),:global(html[data-recipe-print] .breadcrumbs),:global(html[data-recipe-print] .post-meta),:global(html[data-recipe-print] .article-actions),:global(html[data-recipe-print] .related-posts),:global(html[data-recipe-print] .about-card),:global(html[data-recipe-print] .heading-link),:global(html[data-recipe-print] h1:not(.print-title)){display:none!important}
    :global(html[data-recipe-print] .page-layout){display:block!important;max-width:none!important;padding:0!important;margin:0!important}
    :global(html[data-recipe-print]),:global(html[data-recipe-print] body){background:white!important;color:black!important}
  }

  .card-photo{margin:14px 0 0}.card-photo img,.recipe-photo img{display:block;width:100%;height:auto;border-radius:10px}.recipe-photo{max-width:60rem;margin:22px 0}
  @media print{.card-photo,.recipe-photo{display:none!important}}


.meal-library :global([data-slot=checkbox]),:global(.recipe-takeover [data-slot=checkbox]){width:19px;height:19px;min-height:19px;border:1px solid #8b9485;color:white;background:var(--paper);flex-shrink:0}.meal-library :global([data-slot=checkbox][data-state=checked]),:global(.recipe-takeover [data-slot=checkbox][data-state=checked]){background:var(--accent)}.meal-library :global([data-slot=native-select-wrapper]){width:auto;max-width:100%}.family-box :global([data-slot=native-select-wrapper]){width:100%;max-width:360px}.meal-library :global([data-slot=native-select]){background-image:none!important;height:auto}:global([data-slot=dialog-overlay]){background:#0008}
</style>
