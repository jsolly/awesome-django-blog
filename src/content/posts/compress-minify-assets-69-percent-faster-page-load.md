---
slug: compress-minify-assets-69-percent-faster-page-load
title: "Boost Page Speed: Minification and Compression for Static Assets"
category: web-dev
description: "Boost Your Website's Speed: How Compression and Minification Can Help You Reduce Your Payload Size by Up to 40%, For a Faster, More Responsive Website."
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/image_compression_jEj4yMk.png
legacyImage: post_metaimgs/image_compression_jEj4yMk.png
imageAlt: Screenshot of various image files being compressed.
imageAttribution: ""
imageWidth: 408
imageHeight: 219
published: "2022-06-17T12:10:31Z"
updated: "2024-11-06T13:40:23.429Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>Boost Your Website's Speed: How Compression and Minification Can Help You Reduce Your Payload Size by Up to 40%, For a Faster, More Responsive Website.</p>"
legacyId: 68
related:
  - gis-job-search-resources
  - 15-minute-dump-and-go-instant-pot-recipes
  - Adding-views-likes-to-posts
---

Caching static assets is only half the game. Adding minification and compression dramatically boosts page speed. With <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/114">this PR,</a> all CSS/JS is now compressed and minified via <a target="_blank" rel="noopener noreferrer" href="https://whitenoise.evans.io/en/stable/">WhiteNoise</a>, HTML minified via <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/middleware/#module-django.middleware.gzip">GzipMiddleware</a>, and images via <a target="_blank" rel="noopener noreferrer" href="https://imageoptim.com/howto.html">ImageOptim</a>.

## Before Optimization

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_vkktOjM.png" alt="Screenshot of file list before optimization"></figure>

## After making changes with WhiteNoise + GzipMiddleware

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_4BEdjPr.png" alt="Screenshot of files after (size gets smaller)"></figure>

Many of the files are smaller. For example, main.css went from 5.4 kB to 2.1 kB. That’s a -61% decrease in size!

<figure class="table"><table><thead><tr><th>File</th><th>Before</th><th>After</th><th><p>Percent&nbsp;</p><p>Change</p></th></tr></thead><tbody><tr><td>main.css</td><td>5.4 kB</td><td>2.1 kB</td><td><strong>-61% 🔻</strong></td></tr><tr><td>index.html</td><td>16.4 kB</td><td>6.1 kB</td><td><strong>-63%</strong> 🔻</td></tr><tr><td>branding_logo.svg</td><td>15.7 kB</td><td>6.5 kB</td><td><strong>-59%</strong> 🔻</td></tr><tr><td>jsolly.jpeg</td><td>9.6 kB</td><td>9.9 kB</td><td><strong>+3%&nbsp;</strong> &nbsp; &nbsp;&nbsp;<span class="text-big" style="background-color:rgb(247,247,247);color:rgb(65,105,225);">▲</span></td></tr><tr><td>kofi.png</td><td>4.5 kB</td><td>4.8 kB</td><td><strong>+7%</strong> &nbsp; &nbsp; &nbsp;<span class="text-big" style="background-color:rgb(247,247,247);color:rgb(65,105,225);">▲</span></td></tr><tr><td>favicon.png</td><td>1.9 kB</td><td>2.2 lB</td><td><strong>+16%</strong> &nbsp; &nbsp;<span class="text-big" style="background-color:rgb(247,247,247);color:rgb(65,105,225);">▲</span></td></tr></tbody></table></figure>

Unfortunately, images INCREASED in size. Doesn’t appear that WhiteNoise compresses images. That makes sense because image compression degrades quality. A colleague suggested the tool <a target="_blank" rel="noopener noreferrer" href="https://imageoptim.com/howto.html">ImageOptim</a>. ImageOptim reduces file size by removing image metadata.

<blockquote><p>By default ImageOptim removes invisible metadata from images, such as EXIF camera information and color profile. ImageOptim overwrites the files with their optimized versions. This is safe, because ImageOptim preserves image quality.</p></blockquote>

It blows my mind how much the tool reduces image size.

<figure class="table"><table><thead><tr><th>File</th><th>Before</th><th>After</th><th><p>Percent</p><p>Change</p></th></tr></thead><tbody><tr><td>jsolly.jpeg</td><td>9.6 kB</td><td>8.9 kB</td><td><strong>-7% &nbsp;</strong> &nbsp;&nbsp;<strong>🔻</strong></td></tr><tr><td>kofi.png</td><td>4.8 kB</td><td>2.1 kB</td><td><strong>-56%</strong> <strong>🔻</strong></td></tr><tr><td>favicon.png</td><td>2.2 kB</td><td>1 kB</td><td><strong>-55%</strong> <strong>🔻</strong></td></tr></tbody></table></figure>

## Conclusion

With a handful of lines, you can decrease the size of static assets. Additionally, I found a way to reduce image file size without quality loss by removing image metadata via <a target="_blank" rel="noopener noreferrer" href="https://imageoptim.com/howto.html">ImageOptim</a>. By performing these optimizations, the total payload size went from 50.6 kB (not including CDN minified assets) to 30 kB for an overall reduction of 40<strong>%. </strong> For small websites like mine, you might not notice 20 kB, but imagine a large, media-rich site reducing its size by 40%

Add compression and minification to your static assets today!
