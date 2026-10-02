---
slug: Adding-spell-check-django-ckeditor
title: "Enhance Your Blog: Enable Spell Checking With SCAYT in Django CKEditor"
category: web-dev
description: Learn how to enable spell checking in Django CKEditor with SCAYT. This guide will show you how to improve the editing experience on your website.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/spellcheck.webp
legacyImage: post_metaimgs/spellcheck.webp
imageAlt: abc with a green checkmark
imageAttribution: ""
imageWidth: 720
imageHeight: 720
published: "2021-12-31T05:36:14Z"
updated: "2026-09-07T14:25:05.448Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to enable spell checking in Django CKEditor with SCAYT. This guide will show you how to improve the editing experience on your website.</p>
legacyId: 6
related:
  - Adding-code-snippets-ckeditor
  - Adding-views-likes-to-posts
  - migrating-to-ckeditor-5
---

## Note

I wrote this post a while ago and am unsure if this still works. The doc links I used to use now throw a 404. Your mileage may vary.

## Intro

Added an 'All Categories' section to the sidebar and enabled spell checking on <a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/">ckeditor</a>, a WYSIWYF (What you see is what you get) editor. 

Check out this video about how to enable it in a Django project!

<figure class="media"><div data-oembed-url="https://www.youtube.com/embed/ggPfQfuV7rM"><div style="position: relative; padding-bottom: 100%; height: 0; padding-bottom: 56.2493%;"><iframe src="https://www.youtube.com/embed/ggPfQfuV7rM" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0;" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen="" title="Video: Enhance Your Blog: Enable Spell Checking With SCAYT in Django CKEditor"></iframe></div></div></figure>

After scanning through a few Github repos, I came across SCAYT. It's a plugin for django-ckeditor. The installation directions instruct you to clone a repo into the plugins folder, but when I checked that folder, I noticed SCAYT was already there!

Turns out that SCAYT is a plugin that's included by default when you pip install django-ckeditor. I tried finding Youtube videos or guides on how to get it working, but nothing worked for me!

<s>I decided to visit the git repo of django-ckeditor itself&nbsp;and was blessed with great doc on how to do it! All you need do is add&nbsp;CKEDITOR_CONFIGS to the settings.py file.</s> For some reason, they have since deleted this doc.

After adding this code to my django settings file, I got all this new functionality.

<pre><code class="language-python">CKEDITOR_CONFIGS = {
'default': {'toolbar': 'full'},
}</code></pre>

## Before

<img class="image_resized" style="height:420px;width:500px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/before_add_post.png" alt="Create post screen before adding ckeditor">

## After

<img class="image_resized" style="height:495px;width:500px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/after_add_post.png" alt="Create post view after adding ckeditor">

I think there are way too many buttons going on here, but at this point in the website, I am the only one making posts, so I will leave it for now. Plus, it's fun to have so much rich text functionality.

The second problem I ran into is that SCAYT is not enabled by default. You need to click on it and choose 'enable’ start spell checking my posts.

<img class="image_resized" style="height:203px;width:196px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/disable_scaty.png" alt="Disable SCAYT dropdown in ckeditor">

Turns out, there is an option you can set in ckeditor's config.js file which is located in /static/ckeditor/ckeditor/config.js

<code>config.scayt_autoStartup = true;</code>

After adding this property to that file, it now enables on-load!
