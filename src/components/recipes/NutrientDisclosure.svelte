<script>
  import CollapsibleRoot from '$lib/components/ui/collapsible/collapsible.svelte';
  import CollapsibleTrigger from '$lib/components/ui/collapsible/collapsible-trigger.svelte';
  import CollapsibleContent from '$lib/components/ui/collapsible/collapsible-content.svelte';
  import { nutrientAmount } from './nutrition.mjs';
  let { nutrients } = $props();
  const visibleNutrients=$derived(nutrients.filter(n=>n.percent!==0));
  let preview = $derived(visibleNutrients.filter(n => n.percent !== null).sort((a,b) => b.percent-a.percent).slice(0,3).map(n => `${n.label} ${n.percent}% DV`).join(' · '));
</script>

<CollapsibleRoot class="nutrient-disclosure">
  <h4><CollapsibleTrigger class="nutrient-trigger">
    <span>Vitamins &amp; minerals<small>{preview}</small></span>
    <svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>
  </CollapsibleTrigger></h4>
  <CollapsibleContent>
    <dl class="daily-values">{#each visibleNutrients as nutrient (nutrient.key)}<div><dt>{nutrient.label}</dt><dd>{nutrientAmount(nutrient.amount)} {nutrient.unit}<span>{nutrient.percent===null?'—':`${nutrient.percent}% DV`}</span></dd></div>{/each}</dl>
  </CollapsibleContent>
</CollapsibleRoot>

<style>
  :global(.nutrient-disclosure){margin-top:24px;border-top:1px solid var(--recipe-line)}
  h4{margin:0}
  :global(.nutrient-trigger){width:100%;display:flex;align-items:center;justify-content:space-between;gap:16px;text-align:left;border:0;border-radius:6px;background:transparent;color:var(--recipe-ink);padding:14px 4px;font-weight:650!important;font-size:.9rem!important}
  :global(.nutrient-trigger:hover){background:var(--recipe-soft)}
  small{display:block;margin-top:5px;color:var(--recipe-muted);font-size:.76rem;font-weight:400;line-height:1.5}
  svg{flex-shrink:0;transition:transform .2s}
  :global(.nutrient-trigger[data-state=open]) svg{transform:rotate(180deg)}
  dl{display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.84rem;margin-top:4px}
  dl>div{padding:8px;background:var(--recipe-soft);border-radius:6px}
  dt{font-size:.73rem;color:var(--recipe-muted)}
  dd{font-weight:650;margin:2px 0}
  dd span{display:block;font-size:.75rem;font-weight:400;color:var(--recipe-muted)}
  @media(prefers-reduced-motion:reduce){svg{transition:none}}
</style>
