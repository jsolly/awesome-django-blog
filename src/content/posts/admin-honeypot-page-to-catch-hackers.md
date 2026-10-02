---
slug: admin-honeypot-page-to-catch-hackers
title: Securing Your Django Admin Page With django-admin-honeypot
category: web-dev
description: Protect a Django admin page from bots and hackers with django-admin-honeypot. Learn how to implement logging and email notifications of failed login attempts.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/honeypot.jpg
legacyImage: post_metaimgs/honeypot.jpg
imageAlt: A honeypot with a lock on it.
imageAttribution: https://www.helpnetsecurity.com/2020/02/06/detecting-zero-day-iot-exploits/
imageWidth: 1280
imageHeight: 854
published: "2022-05-08T15:15:49Z"
updated: "2026-09-07T14:25:05.471Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Protect a Django admin page from bots and hackers with django-admin-honeypot. Learn how to implement logging and email notifications of failed login attempts.</p>
legacyId: 41
related:
  - migrating-to-django-4x
  - how-to-get-a-perfect-mozilla-observatory-score
  - how-to-ask-questions-like-a-senior-engineer
---

I recently came across this python module, <a target="_blank" rel="noopener noreferrer" href="https://duckduckgo.com/?q=django-admin-honeypot&amp;t=osx&amp;ia=web">django-admin-honeypot</a>, and it's genius! The way django-admin-honeypot works is that it changes the /admin route to a fake login page and logs any login attempts in the database. See <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/pull/39">my PR</a> for more details on the implementation.

Try logging into my admin page with whatever username/password you want.

https://blogthedata.com/admin

I store every login attempt in the database for later review. The username field tells me what username they tried to use (don't worry, I don't know what password you tried).

<img class="image_resized" style="height:231px;width:800px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220508081723-1.png" alt="Django admin page showing an attempted login">

If I want to be extra hardcore, I could use a combination of the admin-honeypot signal hook and a tool like <a target="_blank" rel="noopener noreferrer" href="https://github.com/fail2ban/fail2ban/wiki">fail2ban</a> to block any IP address that tries to login on this page (don't worry, I haven't implemented that, so hack away).

If you add this entry into your signals.py file, you can catch all login attempts to this page with the user's IP address as a local variable. I might add an email notification to my implementation so I get an email as soon as someone tries to login.

<pre><code class="language-python">from admin_honeypot.signals import honeypot
@receiver(honeypot)
def my_callback(sender, **kwargs):
    print("Caught ya!")
    # send an email to the webmaster?</code></pre>

Haven't caught any hackers or bots yet, but was sure fun to implement!
