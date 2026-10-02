---
slug: Migrating-from-apache-to-Nginx-Gunicorn
title: "Switching to Nginx and Gunicorn: Updating My Blog's Web Server"
category: dev-tools
description: Upgrade your server and application with this step-by-step guide on migrating from Apache to Nginx and Gunicorn. Improve website speed and security!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/gunicorn-logo.png
legacyImage: post_metaimgs/gunicorn-logo.png
imageAlt: Meta Image
imageAttribution: ""
imageWidth: 800
imageHeight: 600
published: "2022-06-29T03:30:36.340Z"
updated: "2024-11-06T13:38:17.835Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Upgrade your server and application with this step-by-step guide on migrating from Apache to Nginx and Gunicorn. Improve website speed and security!</p>
legacyId: 69
related:
  - implement-continuous-integration-github-actions
  - how-to-get-a-perfect-mozilla-observatory-score
---

When I first created this blog, I used Apache to handle all the web requests and serve static files. With <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/116">this PR</a> blogthedata.com has a new web server (Nginx) and application server (Gunicorn)!

Here's what I did:

1 - Export blogthedata database from postgres

2 - Shut down existing Ubuntu VM 

3 - Create new Ubuntu VM

4 - Create new DNS A records in Cloudflare to redirect to the new IP address

5 - Follow <a target="_blank" rel="noopener noreferrer" href="https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04">this guide</a> to install all the components.

6 - Re-run <a target="_blank" rel="noopener noreferrer" href="https://certbot.eff.org/">Certbot</a> to install new HTTPS certificates

Done!
