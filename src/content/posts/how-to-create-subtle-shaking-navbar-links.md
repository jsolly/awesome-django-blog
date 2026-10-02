---
slug: how-to-create-subtle-shaking-navbar-links
title: Add a Subtle Shake Effect to Your Website With CSS Animations
category: web-dev
description: Learn how to add a shake effect to any element on your website with CSS animations. Use the prefers-reduced-motion media query to turn off the animation.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/ButtonShake.webp
legacyImage: post_metaimgs/ButtonShake.webp
imageAlt: Meta Image
imageAttribution: CSS keyframe to make button shake
imageWidth: 716
imageHeight: 724
published: "2022-07-23T22:55:58.459Z"
updated: "2022-07-23T22:55:58.459Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to add a shake effect to any element on your website with CSS animations. Use the prefers-reduced-motion media query to turn off the animation.</p>
legacyId: 86
related:
  - three-scenarios-i-dont-use-tailwind
  - cloudflare-minify-optimizations-broke-sri
---

After finishing <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/playlist?list=PL4cUxeGkcC9iGYgmEd2dm3zAKzyCGDtM5">Net Ninja's CSS tutorial</a> on YouTube, I figured out how to add a subtle shake to any element.

<pre><code class="language-css">@keyframes button-shake {
  from {
    rotate:2deg
  }
  to {
    rotate:-2deg
  }
}</code></pre>

This takes the element and rotates it a little bit clockwise and then a little bit counterclockwise. This creates a nice effect on hover.

<pre><code class="language-css">@media (hover: hover) {
 nav a:hover {
 animation: button-shake 0.3s linear;
   }
}</code></pre>

I am nesting it inside<code> @media (hover: hover)</code>because that will limit the animation to only devices that have <code>hover</code> (don't use the animation on mobile). If you don't do this, you'll notice the animation firing off when you tap on an element which looks weird.

With any kind of optional movement on your site, you also should take a look at the <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion">prefers-reduced-motion</a> media query to make sure the animation is turned off for people who have movement sensitivities. All I had to do was add this snippet to my CSS file.

<pre><code class="language-css">@media (prefers-reduced-motion: reduce) {
  nav a:hover {
    animation: none
  }
}</code></pre>

And we're done!
