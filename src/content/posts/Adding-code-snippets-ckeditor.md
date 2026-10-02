---
slug: Adding-code-snippets-ckeditor
title: "Adding Code Snippets to ckeditor: A Step-by-Step Guide"
category: web-dev
description: Learn how to quickly and easily add Code Snippets and plugins to
  ckeditor. Follow this guide to install plugins and format code snippets in
  your blog posts.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/codeSnippets_xpeqEd5.png
legacyImage: post_metaimgs/codeSnippets_xpeqEd5.png
imageAlt: List of languages available to snippet. Python, CSSS, YAML, JSON, Git, SQL
imageWidth: 170
imageHeight: 197
published: 2021-12-31T07:20:23Z
updated: 2021-12-31T02:20:23.123456-05:00
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to quickly and easily add Code Snippets and plugins to
  ckeditor. Follow this guide to install plugins and format code snippets in
  your blog posts.</p>
legacyId: 8
related:
  - Adding-spell-check-django-ckeditor
  - migrating-to-ckeditor-5
  - mastering-intuition-pumps-essential-terms-guide
---
I realized when making posts that ckeditor does not include a code snippets tool. This is useful functionality because it lets you copy/paste code into your post and formats it depending on the language type.

Went over to ckeditor's plugin page and found <a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/docs/ckeditor4/latest/features/codesnippet.html">Code Snippets</a>. Installing it was easy using the <a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/cke4/builder">ckeditor&nbsp;builder</a>. You add all the plugins you want, choose a theme, and download a prepacked .zip file containing everything you need. All you have to do is was copy it into your /static/ckeditor folder.

<pre><code class="language-python">print("Hello World")</code></pre>
