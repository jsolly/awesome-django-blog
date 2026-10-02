---
slug: how-to-implement-subresource-integrity-django
title: "Improving Security With SRI: From F to B on Mozilla Observatory"
category: web-dev
description: Learn how to implement SRI and improve security, including how to generate cryptographic hashes and use the django-sri module | A Step-by-step guide
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/security_hacker.jpg
legacyImage: post_metaimgs/security_hacker.jpg
imageAlt: A hooded man (hacker) pointing at the camera with 0s and 1s
imageAttribution: https://technofaq.org/wp-content/uploads/2016/12/hacker-.jpg
imageWidth: 1920
imageHeight: 1280
published: "2022-05-21T19:42:17Z"
updated: "2024-11-06T13:35:07.129Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to implement SRI and improve security, including how to generate cryptographic hashes and use the django-sri module | A Step-by-step guide</p>
legacyId: 48
related:
  - Adding-views-likes-to-posts
  - smartly-load-CSS-JS-page-load-time
  - how-to-get-a-perfect-mozilla-observatory-score
---

<blockquote><p>Subresource integrity is a recent W3C standard that protects against attackers modifying the contents of JavaScript libraries hosted on content delivery networks (CDNs) in order to create vulnerabilities in all websites that make use of that hosted library.</p><p><a target="_blank" rel="noopener noreferrer" href="https://infosec.mozilla.org/guidelines/web_security#subresource-integrity">Mozilla Infosec</a></p></blockquote>

Earlier this month, I ran a <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-a-perfect-mozilla-observatory-score/">Mozilla Observatory Audit and got an F</a>. I implemented SRI in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/67/files">this PR</a>, which <a target="_blank" rel="noopener noreferrer" href="https://observatory.mozilla.org/analyze/blogthedata.com">upgraded my score to a &nbsp;B</a> !

<img class="image_resized" style="width:586px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220527235214-1.png" alt="Mozilla Observatory security scores. F on May 3rd. B on May 21st.">

To implement SRI, you add a cryptographic hash to each \<link\> and \<script\> tag.

<pre><code class="language-html">&lt;script type='text/javascript' src="{% static 'mailchimp/local-mc-validate.js' %}" integrity="sha384-kNtXczGtgYT982q0agqJfC1hsrUBi3Z3JLr1VrrUIyUZRn2yS6GfAvZ0Dv10mpiy" crossorigin="anonymous"&gt;&lt;/script&gt;</code></pre>

Most of my resources already have integrity values. For example, all <a target="_blank" rel="noopener noreferrer" href="https://getbootstrap.com">bootstrap files served via CDN</a> include SRI protection.

<img class="image_resized" style="width:657px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220527235312-2.png" alt="screenshot of Bootstrap CDN page showing integrity hash">

Still, many dependencies I use do not include it. The CSS/JS for the my code snippets syntax highlighter, <a target="_blank" rel="noopener noreferrer" href="https://prismjs.com">Prism.js</a>, does not come with SRI protection.

Luckily, I discovered <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/django-sri/">django-sri</a> which appears to be the go-to for SRI in Django. For css and .js files, you replace any <code>{% static %}</code> tags with <code>{% sri_static %}</code>. The module generates the whole <code>&lt;script&gt;</code> tag, so

<code>{% sri_static 'local.js' %}</code>

becomes

<code>&lt;script&gt; src="local.js" integrity="&lt;cryptographic-hash&gt;" crossorigin="anonymous"&gt;&lt;/script&gt;</code>

I don’t love this approach because it obfuscates how the resulting HTML will look.

I also encountered problems with django-sri. I couldn't get their hashes to work with my JavaScript files. Every time I used their tag, I got a 500 error on my server and there wasn't anything in the apache error log. The second issue was that django-sri does not seem to work with non-text files. Three of my <code>&lt;link&gt;</code> tags point to favicon .pngs. When hashing these files, django-sri threw uncaught utf-8 parsing errors.

My workaround was to generate the hashes myself using the openssl library.

<pre><code class="language-bash">$ openssl dgst -sha384 -binary prism_patched.min.js | openssl base64 -A</code></pre>

I don't have any strong opinions on hashing algorithms for a personal blog. It's good enough for me that sha384 is a <a target="_blank" rel="noopener noreferrer" href="https://csrc.nist.gov/Projects/Hash-Functions/NIST-Policy-on-Hash-Functions">nist approved hash function</a>.

After generating the hashes, I plugged them into the integrity values manually. The disadvantage is that I'll have to re-compute the hash if I change a resource. Luckily, I don't plan to modify my favicons. They are static assets.

After implementing SRI, I re-ran the Mozilla audit and was still getting flagged for non-compliance. Observatory doesn’t show which resources are missing integrity hashes. Luckily, I came across a GitHub repo called <a target="_blank" rel="noopener noreferrer" href="https://github.com/4armed/sri-check">sri-check</a> put out by a UK-based security company. It's a Python script you can point at any URL to tell you which resources don’t have SRI. It detected a JavaScript file hidden in one of my templates I hadn't hashed. After adding a hash and re-running the Mozilla audit, I got a green check mark and upgraded my score from a D- to B- !!!

## Conclusion

SRI boosts site security by preventing CDN attacks. Many packages, like bootstrap, offer SRI protection out of the box, but I found several dependencies on my site without it. For those CSS/JS files, I hosted them locally on my server. I generated hashes using a combination of the django-sri module and the openssl library. My final security task to get a perfect score on Mozilla Observatory is to <a target="_blank" rel="noopener noreferrer" href="http://github.com/jsolly/awesome-django-blog/issues/41">add&nbsp;a Content security policy</a>. Expect a future post about that adventure!
