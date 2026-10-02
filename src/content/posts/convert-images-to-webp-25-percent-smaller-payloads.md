---
slug: convert-images-to-webp-25-percent-smaller-payloads
title: "Speed Up Your Website With WebP Image Conversion: A Step-by-Step Guide"
category: web-dev
description: Convert your images to WebP for faster website performance. Learn how to use a shell script and see the benefits of WebP's superior compression.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/webpConvert.webp
legacyImage: post_metaimgs/webpConvert.webp
imageAlt: Script for converting images to .webp
imageAttribution: ""
imageWidth: 912
imageHeight: 776
published: "2022-07-28T21:10:31.318Z"
updated: "2022-07-28T21:10:31.318Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Convert your images to WebP for faster website performance. Learn how to use a shell script and see the benefits of WebP's superior compression.</p>
legacyId: 92
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - geospatial-job-interview-tips
  - compress-minify-assets-69-percent-faster-page-load
---

<blockquote><p>WebP is a modern <strong>image format </strong>that provides superior <strong>lossless and lossy</strong> compression for images on the web. Using WebP, webmasters and web developers can create smaller, richer images that make the web faster.</p><p>WebP lossless images are 26% smaller in size compared to PNGs. WebP lossy images are 25-34% smaller than comparable JPEG images at equivalent SSIM quality index.</p><p>-<a target="_blank" rel="noopener noreferrer" href="https://developers.google.com/speed/webp/">Google</a></p></blockquote>

Images are often the largest resource on a site. Making them smaller should be your top priority. To convert my site's images to .webp, I wrote a shell script that recursively traverses the current working directory and all subdirectories to create .webp images out of any pngs, jpegs, and tifs.

<pre><code class="language-bash">#!/bin/bash
PARAMS=('-m 6 -q 70 -mt -af -progress')
if [ $# -ne 0 ]; then
	PARAMS=$@;
fi
shopt -s nullglob nocaseglob extglob
for FILE in $PWD/**/*.@(jpg|jpeg|tif|tiff|png); do 
    cwebp $PARAMS "$FILE" -o "${FILE%.*}".webp;
done</code></pre>

If you place this file in a directory, simply run:

<pre><code class="language-bash">$ bash webp-convert-directory</code></pre>

The script will go through and create .webp files out of all your images. I'm not deleting the original images, but feel free to add that logic in if you want.

Make your website images load 25% faster, today!
