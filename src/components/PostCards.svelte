<script lang="ts">
  import { onMount } from 'svelte';
  export type Card = { slug: string; title: string; description: string; excerpt: string; image: string; imageAlt: string; imageWidth: number | null; imageHeight: number | null; published: string; updated: string; dateLabel: string; updatedLabel: string; category: string; categoryName: string; minutes: number };
  let { posts, pageSize = 0 }: { posts: Card[]; pageSize?: number } = $props();
  let page = $state(1);
  const pages = $derived(pageSize ? Math.max(1, Math.ceil(posts.length / pageSize)) : 1);
  const visible = $derived(pageSize ? posts.slice((page - 1) * pageSize, page * pageSize) : posts);
  onMount(() => {
    const requested = Number(new URLSearchParams(window.location.search).get('page') || 1);
    page = Number.isInteger(requested) ? Math.min(Math.max(requested, 1), pages) : 1;
  });
</script>

<div class="post-list">
  {#each visible as post}
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
  <nav class="pagination" aria-label="Post pages">
    {#if page > 1}<a href={`?page=${page - 1}`}>Previous</a>{/if}
    <span>Page {page} of {pages}</span>
    {#if page < pages}<a href={`?page=${page + 1}`}>Next</a>{/if}
  </nav>
  <noscript><p><a href="/all-posts/">Browse every article without JavaScript</a></p></noscript>
{/if}
