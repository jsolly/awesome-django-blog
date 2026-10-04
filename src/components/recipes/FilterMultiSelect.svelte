<script>
  import PopoverRoot from '$lib/components/ui/popover/popover.svelte';
  import PopoverTrigger from '$lib/components/ui/popover/popover-trigger.svelte';
  import PopoverContent from '$lib/components/ui/popover/popover-content.svelte';
  import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';
  import Button from '$lib/components/ui/button/button.svelte';
  let { label, options, selected = $bindable([]), emptyLabel, disabled=false, canSelect=()=>true } = $props();
  const summary=$derived(selected.length ? selected.map(value=>options[value]).join(', ') : emptyLabel);
  function toggle(value){selected=selected.includes(value)?selected.filter(item=>item!==value):[...selected,value];}
</script>
<div class="filter-select">
  <span class="filter-label">{label}</span>
  <PopoverRoot>
    <PopoverTrigger class="multi-trigger" aria-label={`${label}: ${summary}`} {disabled}>
      <span>{summary}</span><svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m4 6 4 4 4-4"/></svg>
    </PopoverTrigger>
    <PopoverContent class="multi-options" portalProps={{disabled:true}} sideOffset={6} aria-label={`${label} choices`}>
      {#each Object.entries(options) as [value,text] (value)}
        <label><Checkbox checked={selected.includes(value)} disabled={!canSelect(selected.includes(value)?selected.filter(item=>item!==value):[...selected,value])} onCheckedChange={()=>toggle(value)}/>{text}</label>
      {/each}
      <Button variant="outline" type="button" onclick={()=>selected=[]}>Clear selections</Button>
    </PopoverContent>
  </PopoverRoot>
</div>
<style>
  .filter-label{font-size:.86rem;font-weight:600;display:block;margin-bottom:6px}
  :global(.multi-trigger){display:flex;width:100%;align-items:center;justify-content:space-between;gap:12px;min-height:44px;text-align:left;background:var(--recipe-paper,#fffef8);color:var(--recipe-ink,#25392b);border:1px solid var(--recipe-input-border);border-radius:8px;padding:10px;font-size:.86rem!important;font-weight:600}
  :global(.multi-trigger) span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  svg{flex-shrink:0;margin-right:4px}
  :global(.multi-options){z-index:50;background:var(--recipe-paper,#fffef8);color:var(--recipe-ink,#25392b);border:1px solid var(--recipe-input-border);border-radius:10px;padding:10px;width:var(--bits-popover-anchor-width);max-width:calc(100vw - 32px);box-shadow:0 8px 24px #0002}
  label{display:flex;align-items:center;gap:10px;min-height:44px;padding:4px 8px;font-size:.86rem;font-weight:500;cursor:pointer}
  :global([data-slot=checkbox]){width:19px;height:19px;accent-color:var(--recipe-accent);flex-shrink:0}
  :global(.multi-options [data-slot=button]){width:100%;background:transparent;color:inherit;border:1px solid var(--recipe-input-border);border-radius:6px;min-height:44px;font-size:.8rem}
</style>
