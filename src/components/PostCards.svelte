<script lang="ts">
  import { onMount, tick } from 'svelte';
  export type Card = { slug: string; title: string; description: string; excerpt: string; image: string; imageAlt: string; imageWidth: number | null; imageHeight: number | null; published: string; updated: string; dateLabel: string; updatedLabel: string; category: string; categoryName: string; minutes: number };
  let { posts, pageSize = 0 }: { posts: Card[]; pageSize?: number } = $props();
  let page = $state(1);
  const pages = $derived(pageSize ? Math.max(1, Math.ceil(posts.length / pageSize)) : 1);
  const visible = $derived(pageSize ? posts.slice(0, page * pageSize) : posts);
  let sentinel = $state<HTMLDivElement>();
  let automaticBatchesLeft = $state(3);
  let postList = $state<HTMLDivElement>();
  async function loadMore(manual = false) {
    if (page >= pages) return;
    const previousCount = visible.length;
    if (manual) automaticBatchesLeft = 3;
    else automaticBatchesLeft -= 1;
    page += 1;
    const url = new URL(window.location.href);
    url.searchParams.set('page', String(page));
    window.history.replaceState(null, '', url);
    if (manual) {
      await tick();
      postList?.querySelectorAll<HTMLAnchorElement>('.post-card-link')[previousCount]?.focus();
    }
  }
  onMount(() => {
    const requested = Number(new URLSearchParams(window.location.search).get('page') || 1);
    page = Number.isInteger(requested) ? Math.min(Math.max(requested, 1), pages) : 1;
    if (!pageSize || !sentinel || !('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver(entries => {
      if (automaticBatchesLeft > 0 && entries.some(entry => entry.isIntersecting)) void loadMore();
    }, { rootMargin: '200px' });
    observer.observe(sentinel);
    return () => observer.disconnect();
  });
</script>

<div class="post-list" bind:this={postList}>
  {#each visible as post (post.slug)}
    <article class="post-card">
      <a href={`/post/${post.slug}/`} class="card-image" tabindex="-1" aria-hidden="true">
        <img src={post.image} alt={post.imageAlt} width={post.imageWidth ?? undefined} height={post.imageHeight ?? undefined} loading="lazy" decoding="async" />
      </a>
      <div class="card-copy">
        <h2><a class="post-card-link" href={`/post/${post.slug}/`}>{post.title}</a></h2>
        <p class="post-meta"><time datetime={post.published}>{post.dateLabel}</time> in <a href={`/category/${post.category}/`}>{post.categoryName}</a></p>
        {#if post.published.slice(0, 10) !== post.updated.slice(0, 10)}<p class="post-meta">Updated <time datetime={post.updated}>{post.updatedLabel}</time></p>{/if}
        <p class="post-meta">{post.minutes} min read</p>
        {#if post.excerpt}<div class="card-excerpt">{@html post.excerpt}</div>{:else}<p>{post.description}</p>{/if}
      </div>
    </article>
  {/each}
</div>
{#if pageSize && pages > 1}
  <div class="load-more" bind:this={sentinel}>
    <p role="status">Showing {visible.length} of {posts.length} articles</p>
    {#if page < pages}
      <a class="load-more-button" class:paused={automaticBatchesLeft === 0} href={`?page=${page + 1}`} onclick={(event) => { event.preventDefault(); void loadMore(true); }}>Load more posts</a>
    {:else}
      <p>You've reached the end. <a href="#top">Back to top</a></p>
    {/if}
  </div>
  <noscript><p><a href="/all-posts/">Browse every article without JavaScript</a></p></noscript>
{/if}
