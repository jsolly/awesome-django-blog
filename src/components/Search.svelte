<script lang="ts">
  import { onMount } from 'svelte';
  import { z } from 'zod';
  const entry = z.object({ slug: z.string(), title: z.string(), description: z.string(), text: z.string() });
  let query = $state('');
  let index = $state<z.infer<typeof entry>[]>([]);
  let status = $state<'loading' | 'ready' | 'error'>('loading');
  const results = $derived(index.filter(post => {
    const terms = query.trim().toLocaleLowerCase().split(/\s+/u).filter(Boolean);
    const text = `${post.title} ${post.description} ${post.text}`.toLocaleLowerCase();
    return terms.length > 0 && terms.every(term => text.includes(term));
  }));
  async function loadIndex() {
    status = 'loading';
    try {
      const response = await fetch('/search-index.json');
      if (!response.ok) throw new Error(`Search index HTTP ${response.status}`);
      index = z.array(entry).parse(await response.json());
      status = 'ready';
    } catch { status = 'error'; }
  }
  onMount(() => {
    query = new URLSearchParams(window.location.search).get('searched') ?? '';
    void loadIndex();
  });
</script>

<h1>{query ? `You searched for '${query}'` : 'Search posts'}</h1>
<form action="/search/" method="get" role="search" class="search-form search-page-form">
  <label for="article-search">Search articles</label>
  <div><input id="article-search" type="search" name="searched" bind:value={query} placeholder="Title, topic or phrase" /><button type="submit">Search</button></div>
</form>
<div aria-live="polite" aria-busy={status === 'loading'}>
  {#if status === 'loading'}<p>Loading search...</p>
  {:else if status === 'error'}<p>Search couldn't load. <button onclick={loadIndex}>Try again</button> or <a href="/all-posts/">browse all posts</a>.</p>
  {:else if query.trim()}
    <p>{results.length} {results.length === 1 ? 'result' : 'results'}</p>
    {#if !results.length}<p>No articles matched. Try a shorter phrase or another topic.</p>{/if}
    {#each results as post}
      <article class="search-result"><h2><a class="post-card-link" href={`/post/${post.slug}/`}>{post.title}</a></h2><p>{post.description}</p></article>
    {/each}
  {:else}<p>Search titles and article text across the blog.</p>{/if}
</div>
<noscript><p>Search requires JavaScript. <a href="/all-posts/">Browse all posts</a>.</p></noscript>
