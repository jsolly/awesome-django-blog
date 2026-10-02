---
slug: why-I-stopped-using-pip-freeze
title: "Optimizing Your Project's Dependencies: A Guide to Using Pip Freeze"
category: dev-tools
description: Learn how to use pip freeze to create a shortlist of modules for your requirements.txt file and the benefits of using pip to figure out nested dependencies.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/pip_install.jpg
legacyImage: post_metaimgs/pip_install.jpg
imageAlt: Python logo with the words 'pip install'
imageAttribution: https://i.ytimg.com/vi/eJUj9zMHmJc/maxresdefault.jpg
imageWidth: 1280
imageHeight: 720
published: "2022-05-26T14:28:16Z"
updated: "2024-11-06T13:36:39.290Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to use pip freeze to create a shortlist of modules for your requirements.txt file and the benefits of using pip to figure out nested dependencies.</p>
legacyId: 52
related:
  - Achieve-consistent-builds-with-Python-constraints
  - how-to-test-and-debug-django-templates
  - upgrading-to-the-latest-3x-django
---

<pre><code class="language-bash">$ pip freeze &gt; requirements.txt</code></pre>

Pip freeze outputs installed packages to a text file. Besides serializing my project's dependencies, it also includes dependencies of dependencies. For example, here's what blogthedata.com's requirements.txt used to look like:

<pre><code class="language-python"># requirements.txt
asgiref==3.5.1
async-generator==1.10
attrs==21.4.0
beautifulsoup4==4.9.3
black==22.3.0
certifi==2020.12.5
cffi==1.15.0
chardet==4.0.0
charset-normalizer==2.0.12
chromedriver-autoinstaller==0.3.1
click==8.1.3
coverage==6.3.2
cryptography==37.0.2
Django==3.2.13
django-admin-honeypot==1.1.0
django-ckeditor==6.4.1
django-coverage-plugin==2.0.2
django-csp==3.7
django-fastdev==1.7.2
django-js-asset==2.0.0
django-ranged-response==0.2.0
django-robots==5.0
django-simple-captcha==0.5.14
django-sri==0.3.0
filetype==1.0.10
flake8==3.9.2
geckodriver-autoinstaller==0.1.0
h11==0.13.0
idna==2.10
mccabe==0.6.1
mypy-extensions==0.4.3
outcome==1.1.0
pathspec==0.9.0
Pillow==8.3.2
platformdirs==2.5.2
psycopg2==2.9.3
pycodestyle==2.7.0
pycparser==2.21
pyflakes==2.3.1
pyOpenSSL==22.0.0
PySocks==1.7.1
python-dotenv==0.20.0
pytz==2022.1
requests==2.25.1
selenium==4.1.3
six==1.16.0
sniffio==1.2.0
sortedcontainers==2.4.0
soupsieve==2.1
sqlparse==0.4.2
tomli==2.0.1
trio==0.20.0
trio-websocket==0.9.2
typing_extensions==4.2.0
urllib3==1.26.3
wsproto==1.1.0
</code></pre>

It's hard to figure out what my app <i>really</i> requires. The approach I switched to in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/edc447bd2045bd4ea0a1edf7c4e358ae36777b42">this commit</a> is to only include modules that are actually used by my application.

<pre><code class="language-python">black==22.3.0
chromedriver-autoinstaller==0.3.1
coverage==6.3.2
Django==3.2.13
django-admin-honeypot==1.1.0
django-ckeditor==6.4.1
django-coverage-plugin==2.0.2
django-csp==3.7
django-fastdev==1.7.2
django-robots==5.0
django-simple-captcha==0.5.14
django-sri==0.3.0
filetype==1.0.10
flake8==3.9.2
geckodriver-autoinstaller==0.1.0
Pillow==8.3.2
psycopg2==2.9.3
python-dotenv==0.20.0
requests==2.25.1
selenium==4.1.3
</code></pre>

With a shortlist of modules, pip performs the heavy lifting of figuring out nested dependencies. It has the following advantages:

<ol><li>Only include 1st level dependencies, so it’s clear what my project actually relies on.</li><li>If a module removes a&nbsp;sub-dependency in an update, it doesn't stick around in my requirements file.</li><li>Dependencies can change between operating systems.&nbsp;By letting pip figure out sub-dependencies, I guarantee pip installs the&nbsp;correct modules.</li></ol>

What do you think? DM me on Twitter <a target="_blank" rel="noopener noreferrer" href="https://twitter.com/_jsolly">@_jsolly</a> about it!
