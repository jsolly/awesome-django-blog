---
slug: implement-infinite-scroll-in-django-with-htmx
title: Eliminating Duplicate Pages With HTMX Infinite Scrolling
category: web-dev
description: Discover how htmx can be used to improve your website by implementing infinite scrolling, resolving duplication issues and enhancing functionality.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/htmx.webp
legacyImage: post_metaimgs/htmx.webp
imageAlt: HTMX Logo
imageAttribution: ""
imageWidth: 256
imageHeight: 256
published: "2022-10-26T23:41:20.564Z"
updated: "2026-09-07T14:25:05.503Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Discover how htmx can be used to improve your website by implementing infinite scrolling, resolving duplication issues and enhancing functionality.&nbsp;</p>
legacyId: 105
related:
  - optimizing-ahrefs-orphan-pages-duplicate-content
  - get-a-perfect-score-on-seo-tool-ahrefs
  - I-made-my-code-async-its-388-percent-faster
---

## Note

Hey!   
Since this blogpost was written, I created a new and improved way to do infinite scrolling. Check out this YouTube Video to see the latest implementation. 

<figure class="media"><div data-oembed-url="https://youtu.be/Oj1aEz8XsiI"><div style="position: relative; padding-bottom: 100%; height: 0; padding-bottom: 56.2493%;"><iframe src="https://www.youtube.com/embed/Oj1aEz8XsiI" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0;" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen="" title="Video: Eliminating Duplicate Pages With HTMX Infinite Scrolling"></iframe></div></div></figure>

## Legacy Implementation

Htmx superpowers your html, allowing it to do things you would typically have to do in JavaScript. After discovering <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/get-a-perfect-score-on-seo-tool-ahrefs/">issues with duplicate pages</a> due to my pagination implementation, I removed all the duplication with infinite scroll!

Luckily, I came across an <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/watch?v=RacU_1NgVIg">excellent youtube video</a> by bugBytes who walks you through how to pull off infinite scroll with htmx.

I won't bore you with all the details, but I will highlight how I adjusted the implementation to handle category pages.

In bugByte's example, he hardcodes the URL to fetch articles since he is only working with one view:

<pre><code class="language-html language-python">&lt;div hx-get="{% film-list %}?page={{ page_obj.number|add:1 }}" hx-trigger="revealed" hx-swap="afterend" hx-target="this"&gt;
</code></pre>

In my case, posts can come from multiple views. I modified the request to reference a <code>url</code> variable I passed within the view to support more than one view. Notice I replace <code>film-list</code> with <code>url</code>.

<pre><code class="language-html language-python">&lt;div hx-get="{{ url }}?page={{ page_obj.number|add:1 }}" hx-trigger="revealed" hx-swap="afterend" hx-target="this"&gt;
</code></pre>

Within each view, I pass the current path into the template as a context variable:

<pre><code class="language-python">class CategoryView(ListView):
	...
    def get_context_data(self, *args, **kwargs):
        ...
        context["url"] = self.request.path
        return context</code></pre>

This way, the template is always fetching the correct url!

## Conclusion

After running into <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/get-a-perfect-score-on-seo-tool-ahrefs/">issues with duplicate content</a> with my previous pagination implementation, I decided to use htmx to implement infinite scrolling. This resolved the duplication issue and introduced new functionality. I call that a win!

<a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/142/files">See the PR where I implemented infinite scroll.</a>
