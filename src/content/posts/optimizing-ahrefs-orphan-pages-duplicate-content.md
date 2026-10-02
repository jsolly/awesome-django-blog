---
slug: optimizing-ahrefs-orphan-pages-duplicate-content
title: "Ahrefs Website Optimization: Fix Orphan Pages & Duplicate Content"
category: web-dev
description: Audit your website with Ahrefs to fix orphan pages and duplicate content for better UX, higher SEO, and improved performance.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/SeoOptimization.webp
legacyImage: post_metaimgs/SeoOptimization.webp
imageAlt: A laptop with analytics on the screen. A robot hand is on the keyboard.
imageAttribution: "Stable Diffusion 2.1: A computer screen displaying a website's analytics, with a magnifying glass overlaid on top to symbolize the focus on search engine optimization. In the background, a robot works tirelessly to fix errors and improve the website's ranking."
imageWidth: 512
imageHeight: 512
published: "2023-01-09T06:14:18.161Z"
updated: "2023-01-09T06:14:18.161Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Audit your website with Ahrefs to fix orphan pages and duplicate content for better UX, higher SEO, and improved performance.</p>
legacyId: 115
related:
  - get-a-perfect-score-on-seo-tool-ahrefs
  - social-media-share-links-open-graph
---

## Intro

Ahrefs is a software tool that helps improve the performance of websites in search engines. It is commonly used by SEO professionals and digital marketers to address various issues and improve the visibility of their websites. When I used Ahrefs to analyze my website, I initially received a score in the 80s. The primary reasons for this low score were duplicate content and orphan pages. 

The following sections detail how I overcame these issues to achieve a score of 100/100!

<p style="text-align:center;"><strong>Ahrefs Site Audit Score</strong></p>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_MgV8fds.png" alt="screenshot of ahref score of 100/100"></figure>

## Orphan pages

An orphan page is a web page that is not linked to any other pages on a website. Orphan pages are often difficult for users to discover, as they cannot be accessed by clicking on a link from another page on the site. Orphan pages can also be problematic for search engines, as they may not be able to crawl and index these pages, leading to poor visibility in search results.

I recently <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/implement-infinite-scroll-in-django-with-htmx/"> implemented infinite scroll</a> on my website using HTMX, which caused search crawlers problems. They could not detect the presence of certain blog posts because they were only accessible by scrolling. I had difficulty finding a solution to this issue until a friend suggested creating a static page for search engines to understand. This fixed the problem and enabled search crawlers to properly index my blog posts.

Instead of trying to get Googlebot to understand my infinite scrolling, I simply created a separate page, <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/all-posts/">blogthedata.com/all-posts,</a> that contains page-based pagination. After adding this new page, ahrefs recognized it and no longer flags my posts as orphans!

## Duplicate Content

Another issue that lowered my score was that my productivity page was too similar to my \[Home Page\]. This makes sense as they share a lot of content (the home page contains a superset of all blog categories). My options were to differentiate the two pages or make one 'canonical.' 

To mark a page as "canonical" means to specify that a particular URL represents the preferred version of a page. This is often used when a single piece of content is accessible through multiple URLs or when there are multiple pages with similar or duplicate content.

By marking a page as canonical, you can tell search engines which version of the content they should index and show in search results. This can help prevent duplicate content issues, which can negatively affect a website's search engine ranking.

To fix the issue of my productivity page being too similar to my home page, I marked the home page as the preferred version (also known as the "canonical" version) by adding a "canonical" link element to the head of the productivity page. This is done by adding a line of code that looks like this:

<pre><code class="language-html">&lt;link rel="canonical" href="https://www.blogthedata.com/"&gt;</code></pre>

This tells search engines that the home page of my website is the preferred version of the content, and that they should index and display this version in search results.

After resolving the issues of orphan pages and duplicate content, my website's score was at 100%. However, there were still several other issues that I wanted to address, such as redirects, broken pages, and missing or incorrect metadata.

## Let's go even further!

But I didn't stop there. There are a ton of other issues to resolve, such as:

<ul><li>Internal/external redirects (3xx responses)</li><li>Internal/External missing and broken pages (4xx and 5xx)</li><li>Too long/short meta descriptions and titles</li></ul>

### Fixing Bad Links (3xx, 4xx, 5xx)

On January 5th, I added a new category called "resources" to my blog. This category included a number of posts that were originally saved as markdown documents on my local machine. However, these posts contained a large number of broken or outdated links. As shown in the ahrefs audit, several of these external links were returning 3xx, 4xx, and 5xx errors.

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_cmjzHRQ.png" alt="Screenshot of ahrefs showing 17 external 3xx, 8 external 4xx, and 4 external 5xx"></figure>

Fixing the URLs was a relatively simple but a manual process nonetheless. 

### Fixing 3xxx Redirects

There may be a small performance boost to addressing redirect issues on a website. For example, if I include a link on my website to "example.com/foo" and the owner of the site later removes that page and replaces it with "example.com/bar," a user who follows the link from my site to "example.com/foo" would be intercepted by the website and redirected to the new URL, "example.com/bar." This process, known as a 301 redirect, can slightly slow down the user's experience.

On the other hand, if the website owner deleted "example.com/foo" without setting up a redirect, the user would receive a 404 error (page not found) when they try to access the URL. This can be frustrating for users and can lead to a poor user experience.

To avoid these issues, I want to ensure that all internal and external links on my website resolve to valid URLs. For 3xx URLs, I can simply visit the pages and check my network tab to see where the site is redirecting me. For example, the URL "https://protonmail.com/support/knowledge-base/set-up-a-custom-domain/" now points to "https://proton.me/support/custom-domain" after being redirected.

<p style="text-align:center;"><strong>Inspecting the network traffic in the chromium dev tools</strong></p>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_FRT9kjw.png" alt="Screenshot of dev console showing 301 redirect for protonmail"></figure>

The weirdest discovery I made was that ahref's was flagging an external link to mailchimp.com. According to the audit results, it was redirecting (302) to mailchimp.com/fr, the French version of the Mailchimp website.

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_bpSgp0F.png" alt="Screenshot of 302 redirect to French version of Mailchimp"></figure>

It seems that the user agent of the ahrefs bot appears to be coming from France, causing Mailchimp to redirect to the French version of the site. While this may not be a problem, I will contact ahrefs to get their opinion on the matter.

## Fixing 4xx and 5xx bad links

A 4xx error usually indicates that a webpage is either missing or blocked. I either had to remove the link or find an alternative to fix these errors. I resolved all of these errors except for the 403 (Forbidden) errors that ahrefs flagged for a blog post that contained several links to Cloudflare's documentation. These links worked fine when I tried to access them from my blog, but I think ahrefs' bot crawler was being blocked by Cloudflare. In this case, there isn't much I can do to fix the issue, so I plan to submit a bug report to ahrefs in the hope that they can find a solution.

<p style="text-align:center;"><strong>Ahref's Audit reveals links with 403s</strong></p>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_RfZugIM.png" alt="403 (Forbidden) errors with links to Cloudflare docs"></figure>

<h2>&nbsp;</h2>

## Meta descriptions and titles

It's hard to find hard and fast rules on these as Google simply says <a target="_blank" rel="noopener noreferrer" href="https://developers.google.com/search/docs/appearance/snippet#use-quality-descriptions">don't make them too long or too short</a>. Here are ahref's recommendations:

<strong>Meta Descriptions</strong>

<blockquote><p>A general recommendation today is to keep your page description between 110 and 160 characters, although Google can sometimes show longer snippets.</p></blockquote>

<strong>Titles</strong>

<blockquote><p>Generally recommended title length is between 50 and 70 characters (max 600 pixels). Longer titles will be truncated when they show up in the search results.</p></blockquote>

I had to go through dozens of blog posts to address these issues and re-write their titles and meta descriptions. Luckily, I employed ChatGPT to rewrite most of them!

## Conclusion

In conclusion, using Ahrefs to audit my website helped me identify and resolve issues with orphan pages and duplicate content, leading to a score of 100/100. By creating a static page with page-based pagination and marking the home page as the canonical version of the content on my productivity page, I was able to improve the visibility and performance of my website in search engines. Additionally, I addressed issues with redirects, broken pages, and incorrect metadata to further optimize my website. By following these steps, you can also improve the performance of your website in search engines and provide a better experience for users.
