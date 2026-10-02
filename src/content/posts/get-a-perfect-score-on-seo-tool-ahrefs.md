---
slug: get-a-perfect-score-on-seo-tool-ahrefs
title: "Improving Website Health With Ahrefs: A Step-by-Step Guide"
category: web-dev
description: Improve website's health score with Ahrefs and eliminate duplicate pages. Tips on fixing common issues and implementing new features.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/ahrefScore.webp
legacyImage: post_metaimgs/ahrefScore.webp
imageAlt: John Solly Headshot
imageAttribution: ""
imageWidth: 512
imageHeight: 419
published: "2022-10-26T22:43:09.583Z"
updated: "2022-10-26T22:43:09.583Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Improve website's health score with Ahrefs and eliminate duplicate pages. Tips on fixing common issues and implementing new features.</p>
legacyId: 104
related:
  - implement-infinite-scroll-in-django-with-htmx
  - optimizing-ahrefs-orphan-pages-duplicate-content
---

<a target="_blank" rel="noopener noreferrer" href="https://ahrefs.com/">Ahrefs</a> is an SEO tool that identifies issues on your websites, like broken links, missing alt-text, and more. When I first ran the tool, my site got a 44/100 😭

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_ojFXOEx.png" alt="Ahrefs health score of 44/100"></figure>

## Top Issues

Here's a screenshot of the problems Ahrefs encountered on blogthedata.com

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_FwTrFpJ.png" alt="A list of top issues according to ahrefs. The highlight is 215 pages without canonical."></figure>

## Alt-text, H1 tags, meta descriptions/titles

These were pretty straightforward fixes. Images should have alt-text for non-sighted users, and every page should have an H1 tag as the main header.

Meta descriptions and titles are meta tags in \<head\> are used for social media previews and search engines. I needed to finesse mine to ensure they were in the Goldilocks zone, not too long or too short!

## Duplicate Pages Without Canonical

Search engine crawlers treat the same URLs as duplicates if your site supports 'www' and no 'www' (known as the 'apex' domain). For example,

https://www.blogthedata.com 

and

https://blogthedata.com 

Technically, both of those are on separate domains, so I was getting flagged for duplicate content. To resolve this issue, I found <a target="_blank" rel="noopener noreferrer" href="https://developers.cloudflare.com/pages/how-to/www-redirect/">this article</a> by Cloudflare, which walks you through how you can set up bulk redirects, so anyone visiting a 'www' URL gets redirected to one without www (I think it looks cleaner, anyway!)

After implementing bulk redirects, my score skyrocketed to 92/100.

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_y8S5R6S.png" alt="Ahrefs score of 92"></figure>

### Removing the remaining duplicate pages

I wasn't entirely done. I still had 27 pages that were flagged as duplicates. The issue was that the way I was doing pagination resulted in duplicate content. For example,

https://blogthedata.com/productivity?page1

Had a lot of the same headings, meta tags, and text as:

https://blogthedata.com/productivity?page2

I found a few solutions, but I didn't like them. I thought this would be an excellent opportunity to <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/implement-infinite-scroll-in-django-with-htmx/">implement infinite scrolling with htmx</a> so I could do away with pagination. You can reach more about that implementation in the linked post above, but the result was that my duplicate pages went down to ZERO!

## Conclusion

Ahrefs is an excellent tool in your SEO toolbox. I resolved hundreds of errors that improved my site's SEO, accessibility, and performance. Take your site for a spin through Ahrefs and improve your website health!
