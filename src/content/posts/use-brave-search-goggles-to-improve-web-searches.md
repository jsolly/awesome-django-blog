---
slug: use-brave-search-goggles-to-improve-web-searches
title: Optimizing Web Searches With Brave's Search Goggles
category: productivity
description: Learn how to optimize web searches using Brave Search Googles. Create custom re-ranking on top of the Brave search index using rules and filters.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/solly-goggle.webp
legacyImage: post_metaimgs/solly-goggle.webp
imageAlt: Meta Image
imageAttribution: ""
imageWidth: 277
imageHeight: 188
published: "2022-07-19T21:14:13.095Z"
updated: "2022-07-19T21:14:13.095Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to optimize web searches using Brave Search Googles. Create custom re-ranking on top of the Brave search index using rules and filters.</p>
legacyId: 75
related:
  - adding-global-search
  - optimizing-ahrefs-orphan-pages-duplicate-content
  - finding-reliable-information
---

A few months ago, I wrote a post about <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/finding-reliable-information/">how to use search parameters to optimize web searches with DuckDuckGo</a>. I've found a way to incorporate a lot of those ideas automatically in searches using Brave Search Googles.

<blockquote><p>Goggles enable any individual—or community of people—to alter the ranking of Brave Search by using a set of instructions (rules and filters). Anyone can create, apply, or extend a Goggle. Essentially Goggles act as a custom re-ranking on top of the Brave search index.</p><p>- <a target="_blank" rel="noopener noreferrer" href="https://search.brave.com/help/goggles">Brave</a></p></blockquote>

I created two goggles that I use every day to search the web.

<ol><li><a target="_blank" rel="noopener noreferrer" href="https://search.brave.com/goggles?goggles_id=https%3A%2F%2Fraw.githubusercontent.com%2Fjsolly%2Fsolly-brave-search-goggles%2Fmain%2Fgoggles%2Fno_crap.goggle">No Crap goggles</a></li><li><a target="_blank" rel="noopener noreferrer" href="https://search.brave.com/goggles?goggles_id=https%3A%2F%2Fraw.githubusercontent.com%2Fjsolly%2Fsolly-brave-search-goggles%2Fmain%2Fgoggles%2Fno_crap_remove_top1000.goggle">No Crap Goggles + Remove top 1000 websites</a></li></ol>

Both goggles remove copycats (sites that just scrape StackOverflow and re-host) and low-quality sites (W3schools) while boosting .edu and .org, and official documentation sites. The second goggle goes a step further by removing the top 1000 websites on the internet.

Creating a goggle is super easy. Check out the <a target="_blank" rel="noopener noreferrer" href="https://github.com/brave/goggles-quickstart"> quickstart guide</a>.
