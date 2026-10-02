---
slug: migrating-bs4-to-bs5
title: "Migrating From Bootstrap 4 to 5: Refactoring for a Smooth Transition"
category: web-dev
description: Thinking about upgrading Bootstrap in your app? You might want to check out the breaking changes before you do!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/upgrade_0qtiEXj.png
legacyImage: post_metaimgs/upgrade_0qtiEXj.png
imageAlt: Headshot of John Solly
imageAttribution: ""
imageWidth: 1920
imageHeight: 1280
published: "2022-03-15T13:37:45Z"
updated: "2022-03-15T13:37:45Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Thinking about upgrading Bootstrap in your app? You might want to check out the breaking changes before you do!</p>
legacyId: 25
related:
  - how-to-implement-subresource-integrity-django
  - upgrading-to-the-latest-3x-django
  - how-to-get-a-perfect-mozilla-observatory-score
---

I've been wanting to migrate from Bootstrap 4 to Bootstrap 5. One reason for making the jump is that BS5 drops its dependency on JQuery - often the center of security issues.

I thought little of upgrading aside from swapping out CDN JS/CSS files. Upon upgrading, though, my site broke. Dropdowns stopped working, the layout got wonky.

I reverted the commit and checked Bootstrap's excellent doc on <a target="_blank" rel="noopener noreferrer" href="https://getbootstrap.com/docs/5.0/migration/">migrating to BS5</a>. BS5 introduced many breaking changes.

<blockquote><p>Breaking Data attributes for all JavaScript plugins are now namespaced to help distinguish Bootstrap functionality from third parties and your own code. For example, we use <code>data-bs-toggle</code> instead of <code>data-toggle</code>.</p></blockquote>

After refactoring, everything works again 🤞
