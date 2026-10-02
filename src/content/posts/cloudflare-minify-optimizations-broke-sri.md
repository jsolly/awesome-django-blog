---
slug: cloudflare-minify-optimizations-broke-sri
title: Solve CloudFlare's 'Auto Minify' and Subresource Integrity Conflict
category: web-dev
description: Fix CSS and JS breaking on your website caused by CloudFlare's 'auto-minification' by turning off optimizations and implementing minification server side.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/cloudflare_auto_minify.png
legacyImage: post_metaimgs/cloudflare_auto_minify.png
imageAlt: Screenshot of CloudFlare's auto-minify for HTML, CSS, and JS
imageAttribution: ""
imageWidth: 659
imageHeight: 216
published: "2022-05-26T13:45:42Z"
updated: "2026-09-07T14:25:05.478Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Fix CSS and JS breaking on your website caused by CloudFlare's 'auto-minification' by turning off optimizations and implementing minification server side.</p>
legacyId: 51
related:
  - how-to-implement-subresource-integrity-django
  - Migrating-from-apache-to-Nginx-Gunicorn
  - how-to-get-a-perfect-mozilla-observatory-score
---

After <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-implement-subresource-integrity-django/">implementing subresource integrity</a> and <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/free-cdn-for-17x-speed/"> switching over to CloudFlare</a>, I noticed resources like CSS and JavaScript were breaking on my site. I ran into the same issue as <a target="_blank" rel="noopener noreferrer" href="https://valer.dev/posts/subresource-integrity/">this guy</a>. CloudFlare presents these options and I didn't think twice about turning them on.

<img class="image_resized" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/cloudflare_auto_minify.png" alt="CloudFlare interface showing three checkboxes for 'Auto Minify'...HTML, CSS, and JS" width="659" height="216">

Because there's an integrity hash on these files, they fail to load when modified. CloudFlare's 'auto-minification' changes, causing the hash check to fail.

After turning off these optimizations, CSS and JavaScript started loading again (after purging the cache). I still want to minify my CSS and JS, but I'll have to implement it on the server side.
