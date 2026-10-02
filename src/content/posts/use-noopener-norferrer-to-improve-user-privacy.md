---
slug: use-noopener-norferrer-to-improve-user-privacy
title: Protect User Privacy With the Noreferrer and Noopener Link Attributes
category: web-dev
description: Learn how to protect user privacy on your website with HTML link attributes noreferrer and noopener in this informative article.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/noopenerNoreferrer.webp
legacyImage: post_metaimgs/noopenerNoreferrer.webp
imageAlt: A link to example.com with noopener and noreferrer properties
imageAttribution: ""
imageWidth: 1190
imageHeight: 732
published: "2022-07-28T20:25:37.762Z"
updated: "2022-07-28T20:25:37.762Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to protect user privacy on your website with HTML link attributes <code>noreferrer</code> and <code>noopener</code> in this informative article.</p>
legacyId: 91
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - inspiring-aphorisms-axioms
  - finding-reliable-information
---

Today I am going to talk about these three values of the <code>rel</code> attribute for HTML links.

<ul><li>noreferrer</li><li>noopener</li></ul>

I'll point you to <a target="_blank" rel="noopener noreferrer" href="https://blog.templatetoaster.com/noopener-noreferrer/">this article</a> for a deep dive on <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Web/HTML/Link_types/noreferrer">noreferrer</a> and <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Web/HTML/Link_types/noopener">noopener</a> (And I've just linked you to the MDN docs on the attributes).

The gist of them is that they protect users from being tracked across websites. See, whenever a link is clicked, the default behavior is that information about the current window and domain are passed to the target window and target domain. By using these properties together, traffic to linked sites behave like direct traffic instead of backlinks.

For example, if someone clicks on my LinkedIn profile link from the homepage, LinkedIn opens in a new tab.

<pre><code class="language-html">&lt;a href="https://www.linkedin.com/in/jsolly/" rel="noopener noreferrer" target="_blank"&gt;Linkedin&lt;/a&gt;</code></pre>

But from LinkedIn's perspective, it looks like they visited the URL directly (instead of coming from blogthedata.com) because <code>referrer</code> and <code>window.opener</code> are cleared out. This is nice for users because it improves their cross-site privacy.

Add these attributes to external links today to increase the privacy of your users!
