<script lang="ts">
  let { categories, pathname }: { categories: { slug: string; name: string; count: number }[]; pathname: string } = $props();
  let open = $state(false);
  let hydrated = $state(false);
  import { onMount } from 'svelte';
  onMount(() => { hydrated = true; });
</script>

<button class="menu-toggle" aria-expanded={open} aria-controls="mobile-navigation" onclick={() => { open = !open; }} disabled={!hydrated}>Menu</button>
<nav id="mobile-navigation" class:collapsed={hydrated && !open} aria-label="Main navigation">
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
</nav>
