---
slug: social-media-share-links-open-graph
title: Show the Right Image in LinkedIn Posts With the Open Graph Protocol
category: web-dev
description: Make your posts look beautiful on LinkedIn by using the Open Graph Protocol. Learn how to use the protocol and test it with social media post inspectors.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/thumbs_up.png
legacyImage: post_metaimgs/thumbs_up.png
imageAlt: A thumbs up icon
imageAttribution: ""
imageWidth: 1920
imageHeight: 1920
published: "2022-03-25T04:53:54Z"
updated: "2026-09-07T14:25:05.464Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Make your posts look beautiful on LinkedIn by using the Open Graph Protocol. Learn how to use the protocol and test it with social media post inspectors.</p>
legacyId: 29
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - use-noopener-norferrer-to-improve-user-privacy
  - how-to-add-social-share-buttons-to-your-website
---

When a link is shared on LinkedIn, they analyze the HTML content to figure out what image they show in the preview. If an image can’t be found, you end up with a random one from your site, or an ugly default 🤮

It’s easy adding these properties to make your posts beautiful. According to this <a target="_blank" rel="noopener noreferrer" href="https://stackoverflow.com/questions/19632323/default-website-image-for-social-sharing/46139611#46139611">Stack Overflow Post</a>, many social media sites use the <a target="_blank" rel="noopener noreferrer" href="https://ogp.me/#datetime">Open Graph Protocol&nbsp;</a> to search metadata and determine things like what image should be shown in the preview.

To kick the tires on your site, copy/paste a URL to one of your pages into the <a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/post-inspector/inspect/https:%2F%2Fblogthedata.com%2Fpost%2Fgoogle-lighthouse-perfect-score%2F">LinkedIn Post Inspector</a> or the <a target="_blank" rel="noopener noreferrer" href="https://developers.facebook.com/tools/debug/?q=https%3A%2F%2Fblogthedata.com%2Fpost%2Fgoogle-lighthouse-perfect-score%2F"> Facebook Post Inspector</a>. At first nothing picked up from my site, but after implementing this issue, it’s looking a LOT better! I can now choose what image shows up in the preview when posting to LinkedIn!
