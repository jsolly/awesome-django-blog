---
slug: I-replaced-for-loops-with-for-of-loops-cleaner
title: "Cleaner Code: Using for...of Loops in JavaScript"
category: web-dev
description: Learn how to use ES6's for...of loops to clean up your JavaScript code and improve readability. See a real-world example.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/asteroidLasers.webp
legacyImage: post_metaimgs/asteroidLasers.webp
imageAlt: Screenshot of a for loop with a red x and a for of loop with a green checkmark.
imageAttribution: ""
imageWidth: 1164
imageHeight: 840
published: "2022-08-01T19:58:51.937Z"
updated: "2022-08-01T19:58:51.937Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to use ES6's for...of loops to clean up your JavaScript code and improve readability. See a real-world example.</p>
legacyId: 93
related:
  - how-to-add-leaflet-js-maps-inside-a-django-site
  - TypeScript-revealed-210-issues-JavaScript-codebase
  - migrating-portfolio-from-django-to-astro-js
---

You probably recognize this way of iterating in JavaScript

<pre><code class="language-typescript language-javascript">for (let i = 0; i &lt; myArray.length; i++) {
// do something with myArray[i]
}</code></pre>

in <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of">ES6</a>, there's a much cleaner way with for..of loops

<pre><code class="language-typescript language-javascript">for (item of myArray) {
    // do something with item</code></pre>

I think that looks a lot better! I changed several of my for loops to for...of loops in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoAsteroids/commit/8eff2c9c86eb6943a1dae8b2c0a9fc37afdb368f">this commit</a>.
