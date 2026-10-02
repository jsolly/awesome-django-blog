<script lang="ts">
  let { categories }: { categories: { slug: string; name: string; count: number }[] } = $props();
  let open = $state(false);
  let hydrated = $state(false);
  import { onMount } from 'svelte';
  onMount(() => { hydrated = true; });
</script>

<button class="menu-toggle" aria-expanded={open} aria-controls="mobile-navigation" onclick={() => { open = !open; }} disabled={!hydrated}>Menu</button>
<nav id="mobile-navigation" class:collapsed={hydrated && !open} aria-label="Main navigation">
  <a href="/all-posts/">All posts</a>
  <a href="/rss/">RSS</a>
  <a href="https://github.com/jsolly/awesome-django-blog">GitHub</a>
  <div class="mobile-categories">
    {#each categories as category}
      <a href={`/category/${category.slug}/`}>{category.name} <span>{category.count}</span></a>
    {/each}
  </div>
</nav>
