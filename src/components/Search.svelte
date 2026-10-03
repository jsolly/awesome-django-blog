<script lang="ts">
  import { onMount } from 'svelte';
  import { z } from 'zod';
  import { searchEntry, createArticleSearch } from '../lib/search';
  let query = $state('');
  type SearchState = { kind: 'loading' } | { kind: 'error' } | { kind: 'ready'; search: ReturnType<typeof createArticleSearch> };
  let searchState = $state<SearchState>({ kind: 'loading' });
  const results = $derived(searchState.kind === 'ready' ? searchState.search(query) : []);
  async function loadIndex() {
    searchState = { kind: 'loading' };
    try {
      const response = await fetch('/search-index.json');
      if (!response.ok) throw new Error(`Search index HTTP ${response.status}`);
      const entries = z.array(searchEntry).parse(await response.json());
      searchState = { kind: 'ready', search: createArticleSearch(entries) };
    } catch { searchState = { kind: 'error' }; }
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
<div aria-live="polite" aria-busy={searchState.kind === 'loading'}>
  {#if searchState.kind === 'loading'}<p>Loading search...</p>
  {:else if searchState.kind === 'error'}<p>Search couldn't load. <button onclick={loadIndex}>Try again</button> or <a href="/all-posts/">browse all posts</a>.</p>
  {:else if query.trim()}
    <p>{results.length} {results.length === 1 ? 'result' : 'results'}</p>
    {#if !results.length}<p>No articles matched. Try a shorter phrase or another topic.</p>{/if}
    {#each results as post (post.slug)}
      <article class="search-result"><h2><a class="post-card-link" href={`/post/${post.slug}/`}>{post.title}</a></h2><p>{post.description}</p></article>
    {/each}
  {:else}<p>Search titles and article text. Partial words and small typos work too.</p>{/if}
</div>
<noscript><p>Search requires JavaScript. <a href="/all-posts/">Browse all posts</a>.</p></noscript>
