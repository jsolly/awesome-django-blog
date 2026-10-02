---
slug: google-lighthouse-perfect-score
title: "Getting a Near-Perfect Google Lighthouse Score: Here's How I Did It"
category: web-dev
description: Boost your Google Lighthouse score to near perfect by adding alt-text to images, using natural aspect ratios and explicit image dimensions, and more.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/google_lighthouse_score.png
legacyImage: post_metaimgs/google_lighthouse_score.png
imageAlt: Very high Google Lighthouse scores.
imageAttribution: ""
imageWidth: 423
imageHeight: 179
published: "2022-03-18T01:53:07Z"
updated: "2022-03-18T01:53:07Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Boost your Google Lighthouse score to near perfect by adding alt-text to images, using natural aspect ratios and explicit image dimensions, and more.</p>
legacyId: 27
related:
  - google-lighthouse-audit
  - How-Ive-made-blogthedata-more-accessible
  - social-media-share-links-open-graph
---

Recently ran a <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/google-lighthouse-audit/">Google Lighthouse audit</a> receiving an overall score of 91%. After making changes, it's now a near-perfect score!

## Before

<img class="image_resized" style="height:174px;width:426px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220317151807-1.png" alt="Google Lighthouse Score before. Performance = 98, A11Y = 86, Best Practices = 92, SEO=90">

## After

<img class="image_resized" style="height:179px;width:423px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220317151807-2.png" alt="Google Lighthouse Score after. Performance = 99, A11Y = 100, Best Practices = 100, SEO=100">

Here are the changes I made to boost my score:

1 - Add alt-text to images

Pretty straightforward. Find all \<img\> tags and include alt-text in each one. Alt-text is a key element for accessibility, allowing visual content to be read by screen readers. 

It surprised me that <a target="_blank" rel="noopener noreferrer" href="https://mailchimp.com/">Mailchimp</a>, a 3rd party embedded subscription service, does not add alt-text to its referer banner. I will reach out to Mailchimp to ask why!

2 - Use 'natural' aspect ratios and explicit image dimensions

Several images had 'unnatural' aspect ratios; The width was out of proportion to the height. My profile picture was 64x54 resized within the html to be 64x64. Google didn't like it. I could either make the original image a perfect square, or stick with 64x54 - I took the easy route and just modified the resize params.

There were also images with no size attributes. With no explicit size, the browser 'shifts' the page to create room because it doesn't know how much space it will occupy on the page until render time. This increases your <a target="_blank" rel="noopener noreferrer" href="https://web.dev/cls/">Cumulative Layout Shift</a> (CLS), negatively impacting SEO.

Which reminds me of this GIF

<img class="image_resized" style="height:301px;width:530px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220317155701-3.gif" alt="Meme of trying to click on a button and an ad moves it to the wrong button.">

3 - Minor UI changes

Added lang="en" to the html tag and adjusted componet colors to increase contrast. Check out the difference in my navbar!

## Before

<img class="image_resized" style="height:63px;width:995px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220317160237-6.png" alt="Navbar before showing low contrast.">

## After (Higher contrast)

<img class="image_resized" style="height:56px;width:1090px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220317160207-5.png" alt="Navbar after showing better contrast">

Run a Lighthouse audit on your site and see what you can improve!
