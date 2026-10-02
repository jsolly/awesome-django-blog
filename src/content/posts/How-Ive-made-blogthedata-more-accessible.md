---
slug: How-Ive-made-blogthedata-more-accessible
title: Improving Web Accessibility With Figma Wireframes
category: web-dev
description: Improve website accessibility by adding alt text, increasing contrast, implementing semantic HTML, using Figma wireframes, adding landmark elements, and more!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/a11ylogo_highres.webp
legacyImage: post_metaimgs/a11ylogo_highres.webp
imageAlt: A black circle with the text 'Accessibility' showing an eye, hand, ear, and brain representing different facets of a11y.
imageAttribution: https://staff.washington.edu/tft/a11ylogo/images/a11ylogo_highres.png
imageWidth: 1080
imageHeight: 1080
published: "2022-08-10T05:03:02.336Z"
updated: "2024-11-06T13:37:19.147Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Improve website accessibility by adding alt text, increasing contrast, implementing semantic HTML, using Figma wireframes, adding landmark elements, and more!</p>
legacyId: 97
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - google-lighthouse-audit
  - smartly-load-CSS-JS-page-load-time
---

The journey began when I ran my <a target="_blank" rel="noopener noreferrer" href="https://www.blogthedata.com/post/google-lighthouse-audit/">first Google Lighthouse test</a> and scored 86% for A11Y (Accessibility). From there, I added alt text to all my images and increased the contrast in several areas. This <a target="_blank" rel="noopener noreferrer" href="https://www.blogthedata.com/post/google-lighthouse-perfect-score/">brought my score to 100</a>, but I would hardly call my site accessible at that point.

I recently read through <a target="_blank" rel="noopener noreferrer" href="https://www.w3.org/TR/WCAG21/">WCAG 2.1.</a> Okay, I didn't read it cover-to-cover but combined with a few Youtube videos and <a target="_blank" rel="noopener noreferrer" href="https://www.w3.org/WAI/ER/tools/">several additional automated tools recommended by W3</a>, I found more ways to increase accessibility.

The primary issue with my site was that I was not correctly implementing <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Glossary/Semantics">semantic HTML</a>. Turns out elements like \< h1 \> and \< h2 \> don't just change font-size; They provide meaningful structure to the page, allowing search crawlers, power users, and the visually impaired to navigate a site.

After creating a <a target="_blank" rel="noopener noreferrer" href="https://www.figma.com/file/lHjKaJtWliOr6wLOetKDtJ/BlogtheData-Home?node-id=0%3A1">wireframe of my site in Figma</a>, I added <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/ac5eeccc2da2eb1d060240ef5f613715e6d5eb3c">landmark elements</a>, ensured my <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/07f25bc6ba2605eaba0fa51655780ef41e7e7b40">headings followed a sequential order,</a> and added a few nice-to-haves like a <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/a0d76729840a2f3331eb4aee8522cc61969ecae6">skip link</a> to allow keyboard users to skip over the nav right into the main content of the page.

<p style="text-align:center;">Figma wireframe of blogthedata.com's homepage</p>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_jwvYXCX.png" alt="Figma wireframe showing landmark elements on blogthedata.com's homepage."></figure>

Although never finished, I think I've made great strides toward a more accessible website!
