---
slug: google-lighthouse-audit
title: Optimizing Your Website's Performance With a Google Lighthouse Audit
category: web-dev
description: Improve website performance with Google Lighthouse Audit. Learn how to increase mobile and desktop scores for Performance, A11Y, Best Practices, and SEO.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/google_lighthouse_score_41bEKet.png
legacyImage: post_metaimgs/google_lighthouse_score_41bEKet.png
imageAlt: Headshot of John Solly
imageAttribution: ""
imageWidth: 423
imageHeight: 179
published: "2022-03-15T02:18:32Z"
updated: "2022-03-15T02:18:32Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Improve website performance with Google Lighthouse Audit. Learn how to increase mobile and desktop scores for Performance, A11Y, Best Practices, and SEO.</p>
legacyId: 24
related:
  - google-lighthouse-perfect-score
  - How-Ive-made-blogthedata-more-accessible
---

Google Lighthouse is a developer tool available in Chrome that provides scores related to Performance, A11Y (Accessibility), Best Practices, and SEO (Search Engine Optimization).

You run the audit on any site by opening the dev tools and clicking on 'Generate Report' within the Lighthouse tab.

![Google Lighthouse Audit Generate Report Screen](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220314190140-1.png)

## Blogthedata.com Mobile score

<img class="image_resized" style="height:174px;width:512px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220314190548-3.png" alt="Mobile Score for Google Lighthouse. 98 for performance. 86 for A11y, and 92 for best practices">

## Blogthedata.com Desktop score

<img class="image_resized" style="height:191px;width:516px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220314190615-4.png" alt="Desktop Score for Google Lighthouse. 100 for performance. 86 for A11y, and 92 for best practices">

Not too shabby!

To increase the score, Lighthouse provides a laundry list of 'opportunities' you can leverage. For example, Time to first paint reduces by half a second if I defer loading CSS and JavaScript.

<img class="image_resized" style="height:425px;width:526px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220314190954-5.png" alt="Eliminate render-blocking resources opportunity. Defer CSS and Javascript to improve load time by 0.41 seconds.">

In terms of A11Y, it found a few things. I thought I added alt-text to all images, but forgot to add alt-text to my profile photo!

<img class="image_resized" style="height:296px;width:530px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220314191322-6.png" alt="Avatar images do not have alt-text. Google Lighthouse opportunity">

I made improvements to the look and feel, but the contrast isn't high enough for certain users. I’ll adjust colors to get something that works for all users and still looks good.

<img class="image_resized" style="height:254px;width:516px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220314191539-7.png" alt="Background and Foreground colors do not produce enough contrast. Google Lighthouse opportunity. ">

My colleague Karl Frantz says high-performing teams are ones that see A11Y compliance as a design challenge instead of a burden. I agree and am excited about making blogthedata.com more accessible!

Stay tuned for more adventures where I try to improve Lighthouse scores!
