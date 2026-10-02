---
slug: security-txt-allows-researches-to-contact-you
title: "Secure Website With security.txt: Fight Web Vulnerabilities"
category: web-dev
description: Learn how to create a security.txt file, understand its importance, and generate a GPG asymmetric key pair. FANG companies did it, so should you!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/report_bugs.png
legacyImage: post_metaimgs/report_bugs.png
imageAlt: Bug with bomb legs. Report bugs, observe, verify,  inform
imageAttribution: http://flickr.com/photos/kaet44/
imageWidth: 1456
imageHeight: 1536
published: "2022-05-08T03:29:59Z"
updated: "2022-05-08T03:29:59Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to create a security.txt file, understand its importance, and generate a GPG asymmetric key pair. FANG companies did it, so should you!</p>
legacyId: 40
related:
  - help-google-spider-with-sitemaps-and-robots-file
  - how-to-get-a-perfect-mozilla-observatory-score
  - finding-reliable-information
---

Two days ago, I talked about <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/help-google-spider-with-sitemaps-and-robots-file/">adding a robots.txt file to your site</a> to inform web crawlers like Googlebot for better Google search indexing of your website. Today, <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/pull/53/files">with this PR</a>, I have added a security.txt file to blogthedata.com, giving security researchers a way to contact me about new web services vulnerabilities potentially affecting my site.

It’s easy to set this up yourself! You're adding two routes to your app containing information about how to contact you.

<a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/pgp-key.txt">https://blogthedata.com/pgp-key.txt</a>

<a target="_blank" rel="nofollow">https://blogthedata.com/.well-known/security.txt</a>

<blockquote><p>“When security risks in web services are discovered by independent security researchers who understand the severity of the risk, they often lack the channels to disclose them properly. As a result, security issues may be left unreported. security.txt defines a standard to help organizations define the process for security researchers to disclose security vulnerabilities securely.”</p><p><a target="_blank" rel="noopener noreferrer" href="https://securitytxt.org">https://securitytxt.org</a></p></blockquote>

The first step is to fill out a form on <a target="_blank" rel="noopener noreferrer" href="https://securitytxt.org">https://securitytxt.org</a>. The tricky part is the encryption section. It's asking for the public key of a GPG <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/watch?v=AQDCe585Lnc">asymmetric key pair</a>. There are smarter ways of generating keys, but I used this <a target="_blank" rel="noopener noreferrer" href="https://www.igolder.com/PGP/generate-key/">online PGP generator</a>. Once you create the keys, you'll want to stash the private key somewhere safe and put your public key at a publically accessible endpoint. 

Add a security.txt file to your website and join companies like <a target="_blank" rel="noopener noreferrer" href="https://www.google.com/.well-known/security.txt">Google</a>, <a target="_blank" rel="noopener noreferrer" href="https://www.facebook.com/.well-known/security.txt">Facebook</a>, and <a target="_blank" rel="noopener noreferrer" href="https://github.com/.well-known/security.txt">Github</a> to make the web safer for everyone.
