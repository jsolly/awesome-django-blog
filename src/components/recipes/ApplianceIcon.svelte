<script>
  let { name, decorative=false } = $props();
</script>

<svg viewBox="0 0 32 32" width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" role={decorative?undefined:"img"} aria-hidden={decorative} aria-label={decorative?undefined:name}>
  <title>{name}</title>
  {#if name === 'Oven'}
    <rect x="4" y="3" width="24" height="26" rx="3"/><path d="M4 10h24M9 7h.1M16 7h.1M23 7h.1"/><rect x="8" y="14" width="16" height="11" rx="1"/><path d="M12 17h8"/>
  {:else if name === 'Two air fryers' || name === 'Air fryer'}
    <rect x="5" y="3" width="22" height="26" rx="5"/><path d="M12 8h8M7 14h18M14 18h4v6h-4z"/>
  {:else if name === 'Blender'}
    <path d="M9 3h14l-2 16H11zM12 19h8l4 10H8zM23 6h4v9h-5M12 9h4M12 13h4"/><circle cx="16" cy="25" r="1"/>
  {:else if name === 'Pans'}
    <path d="M3 15h17v3a7 7 0 0 1-7 7h-3a7 7 0 0 1-7-7zM20 17l10-4M8 7v4M13 5v6"/>
  {:else if name === 'Microwave'}
    <rect x="2" y="7" width="28" height="19" rx="3"/><rect x="6" y="11" width="15" height="11" rx="1"/><path d="M25 12h1M25 16h1M25 20h1M8 29h16"/>
  {:else}
    <path d="M7 11h18v13a4 4 0 0 1-4 4H11a4 4 0 0 1-4-4zM5 11h22M10 7h12l3 4M13 4h6v3M3 15h4M25 15h4"/><rect x="12" y="17" width="8" height="6" rx="1"/>
  {/if}
</svg>

<style>svg{display:block;flex-shrink:0}</style>
