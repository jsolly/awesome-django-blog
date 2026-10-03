<script lang="ts">
  import Button from '../lib/components/ui/button/button.svelte';
  import Input from '../lib/components/ui/input/input.svelte';
  let { categories, pathname }: { categories: { slug: string; name: string; count: number }[]; pathname: string } = $props();
  let open = $state(false);
  let hydrated = $state(false);
  import { onMount } from 'svelte';
  let mobile = $state(false);
  onMount(() => {
    const query = window.matchMedia('(max-width: 900px)');
    const update = () => { mobile = query.matches; };
    update();
    query.addEventListener('change', update);
    hydrated = true;
    return () => query.removeEventListener('change', update);
  });
</script>

<Button class="menu-toggle" aria-expanded={open} aria-controls="mobile-navigation" onclick={() => { open = !open; }} disabled={!hydrated} aria-label={open ? 'Close menu' : 'Open menu'}>
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
    <path class="menu-line top" d="M3 6h18" />
    <path class="menu-line middle" d="M3 12h18" />
    <path class="menu-line bottom" d="M3 18h18" />
  </svg>
</Button>
<div id="mobile-navigation" class="navigation-panel" class:collapsed={!open} inert={mobile && hydrated && !open}>
<nav aria-label="Main navigation">
  <a href="/all-posts/">All posts</a>
  <a href="/rss/">RSS</a>
  <a href="https://github.com/jsolly/awesome-blog">GitHub</a>
  <details class="category-menu">
    <summary>Categories</summary>
    <div class="category-options">
      <a href="/" aria-current={pathname === '/' ? 'page' : undefined}>Blog home</a>
    {#each categories as category (category.slug)}
      <a href={`/category/${category.slug}/`} aria-current={pathname === `/category/${category.slug}/` ? 'page' : undefined}>{category.name} <span>{category.count}</span></a>
    {/each}
    </div>
  </details>
  <form action="/search/" method="get" role="search" class="search-form">
    <label class="visually-hidden" for="site-search">Search</label>
    <Input id="site-search" type="search" name="searched" placeholder="Search posts..." /><Button type="submit">Search</Button>
  </form>
</nav>
</div>
