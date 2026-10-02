---
slug: adding-slugified-urls
title: "Adding Slugified URLs: A Step-by-Step Guide to Updating Your URLs"
category: web-dev
description: Learn how to add slugified URLs to your website by updating templates and views. Follow this step-by-step guide for easy implementation.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/banana-slug.jpeg
legacyImage: post_metaimgs/banana-slug.jpeg
imageAlt: A banana slug
imageAttribution: ""
imageWidth: 1920
imageHeight: 1280
published: "2022-02-02T15:38:26Z"
updated: "2022-02-02T15:38:26Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to add slugified URLs to your website by updating templates and views. Follow this step-by-step guide for easy implementation.</p>
legacyId: 15
related:
  - adding-global-search
  - google-lighthouse-perfect-score
  - Adding-spell-check-django-ckeditor
---

As of today, each post's url in the address bar is a slug such as 'adding-slugified-urls' instead of the post id...e.g.

post/15

This improves SEO (and makes the share links a lot more comprehensible). This involved modifying A LOT of files and broke tons of stuff before I fixed it. Here is an example of how my urls.py changed:

<img class="image_resized" style="height:285px;width:1307px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/slugified_code_changes.png" alt="Code changes needed to slugify posts. The left side of the image shows the before and the right side shows the after.">

After adding a new slug field to the post model, you add it to the post form as a text field. This allows you  to set the slug to whatever you want.

<img class="image_resized" style="height:351px;width:942px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/create_post_slug_field.png" alt="Create post view showing slug field">

Because the url changes, you need to update all of your templates so the hrefs to posts reference the post.slug instead of post.id.

Finally, an update to views.py file ensures a db lookup of a post used the slug for a unique lookup instead of the post id.

<code>post = Post.objects.get(slug=self.object.slug)</code>

Everything seems works so far!
