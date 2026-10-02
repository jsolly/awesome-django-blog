---
slug: Achieve-consistent-builds-with-Python-constraints
title: "Streamlining Dependency Management: Using Constraints Files in Django"
category: dev-tools
description: "Use a constraints.txt file with pip install to ensure sub-dependencies won't break your app: A guide to set up requirements.txt and constraints.txt files."
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/python_logo_RINquiv.png
legacyImage: post_metaimgs/python_logo_RINquiv.png
imageAlt: Python Logo
imageAttribution: ""
imageWidth: 1280
imageHeight: 800
published: "2022-07-11T00:49:45.283Z"
updated: "2024-12-23T23:19:48.808Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>Use a constraints.txt file with pip install to ensure sub-dependencies won't break your app: A guide to set up requirements.txt and constraints.txt files.</p>"
legacyId: 72
related:
  - why-I-stopped-using-pip-freeze
  - implement-continuous-integration-github-actions
  - upgrading-to-the-latest-3x-django
---

<blockquote><p>Constraints files are requirements files that only control which version of a requirement is installed, not whether it is installed or not.</p><p>- <a target="_blank" rel="noopener noreferrer" href="https://pip.pypa.io/en/stable/user_guide/#constraints-files">Pip documentation</a></p></blockquote>

In a <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/why-I-stopped-using-pip-freeze/">previous post</a>, I talked about ditching pip freeze because it didn't work well with second-level dependencies (especially cross-platform). I found an even better workflow where I use a requirements.txt and a constraints.txt file together. Check out the code in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/b4e10f7f2e8ac7ce69233d26e0ffa593af3ad6f7">this commit</a>.

<pre><code class="language-bash">requirements
├── constraints.txt
└── requirements.txt</code></pre>

Just add a second flag to pip install.

<pre><code class="language-python">python3 -m pip install -r requirements.txt -c constraints.txt</code></pre>

Inside <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/blob/master/requirements.txt">requirements.txt </a> are packages blogthedata directly uses. 

<pre><code class="language-bash"># requirements.txt
black
Brotli
chromedriver-autoinstaller
coverage
Django
...</code></pre>

Constraints.txt  includes everything in requirements.txt plus sub-dependencies

<pre><code class="language-python"># constraints.txt
black==22.3.0
Brotli==1.0.9
cachetools==5.2.0
certifi==2022.6.15
cffi==1.15.1
...</code></pre>

When used together, we are instructing pip to install everything in requirements.txt with the constraint that if anything is installed that is listed in constraints.txt, use the pinned version.

Now I can be certain sub-dependencies won't break my app without requiring that the sub-dependencies be installed.
