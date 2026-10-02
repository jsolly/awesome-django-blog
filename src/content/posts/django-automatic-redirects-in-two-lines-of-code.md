---
slug: django-automatic-redirects-in-two-lines-of-code
title: Fixing Broken Links With Django's Redirects App
category: web-dev
description: Learn how to use the redirects app in Django to redirect old URLs to new ones, avoiding 404 errors | A guide
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/django.webp
legacyImage: post_metaimgs/django.webp
imageAlt: Lead actor of Django Unchained pointing a gun at the camera
imageAttribution: ""
imageWidth: 1400
imageHeight: 984
published: "2022-07-24T22:09:57.597Z"
updated: "2022-07-24T22:09:57.597Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to use the redirects app in Django to redirect old URLs to new ones, avoiding 404 errors | A guide</p>
legacyId: 88
related:
  - how-I-present-portfolio-projects-to-impress
  - 12-questions-you-should-ask-at-your-next-interview
  - mastering-intuition-pumps-essential-terms-guide
---

Let's say you make a post about your favorite color.

<code>/red-is-my-favorite-color</code>

Time passes, and you decide red isn't so hot anymore. Now your favorite color is blue. So you change the slug.

<code>/blue-is-my-favorite-color</code>

But now everyone who visits the original link gets a 404. To fix that up, I followed the <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/contrib/redirects/">Django Docs</a> and added the redirects app to my Django project in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/commit/2524fb88d9f56ef5b80a868041149428b12760bc">this commit</a>. as of July 2022, all you have to do is:

<ol><li>Ensure that the django.contrib.sites framework is installed.</li><li>Add 'django.contrib.redirects' to your INSTALLED_APPS setting.</li><li>Add 'django.contrib.redirects.middleware.RedirectFallbackMiddleware' to your MIDDLEWARE setting.</li><li>Run the command manage.py migrate.</li></ol>

Now on your admin page, you can add all the redirects you want

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_qzOXJUh.png" alt="screenshot of redirect page showing /red-is-my-favorite-color redirecting to /blue-is-my-favorite-color"></figure>

I could add something in signals.py to do this automatically on slug change, but I don't want this behavior to be automagic, and I don't change link slugs very often.

Hope that was useful to you 😁
