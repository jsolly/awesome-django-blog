---
slug: migrating-to-ckeditor-5
title: "Demystifying the CKEditor 4 to 5 Migration Process: Lessons Learned"
category: web-dev
description: Learn how to migrate from CKEditor 4 to CKEditor 5 and strengthen your Content Security Policy (CSP) by removing unsafe-inline scripts | A Guide
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/toad.jpg
legacyImage: post_metaimgs/toad.jpg
imageAlt: A picture of a toad chilling in the sand.
imageAttribution: ""
imageWidth: 1920
imageHeight: 1280
published: "2022-05-27T18:45:25Z"
updated: "2022-05-27T18:45:25Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to migrate from CKEditor 4 to CKEditor 5 and strengthen your Content Security Policy (CSP) by removing unsafe-inline scripts | A Guide</p>
legacyId: 54
related:
  - smartly-load-CSS-JS-page-load-time
  - how-to-implement-content-security-policy-django
  - how-to-ask-questions-like-a-senior-engineer
---

<p style="margin-left:0px;">Migrating ckeditor4 to CKEditor is not straightforward.</p>

<blockquote><p style="margin-left:0px;"><i>When compared to its predecessor, CKEditor 5 should be considered <strong>a totally new editor</strong>. Every single aspect of it was redesigned — from installation, to integration, to features, to its data model, and finally to its API. Therefore, moving applications using a previous CKEditor version to version 5 cannot be simply called an "upgrade". It is something bigger, so the "migration" term fits better.</i></p><p style="margin-left:0px;"><a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/docs/ckeditor5/latest/installation/getting-started/migration-from-ckeditor-4.html"><i>Ckeditor5 Migration Doc</i></a></p></blockquote>

<p style="margin-left:0px;">I moved to CKEditor 5 to overcome roadblocks hit while <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-implement-content-security-policy-django/">implementing a CSP (content security policy</a>). Ckeditor4 uses unsafe-inline styling and scripts, which weaken a CSP. I noticed active work on a new Python module, <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/django-ckeditor-5/">django-ckeditor-5</a>, so I created a branch and started experimenting.</p>

<h2 style="margin-left:0px;">Existing Plugins</h2>

<figure class="table"><table style="border:1px solid black;"><tbody><tr><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">Ckeditor 4</p></td><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">CKEditor 5</p></td></tr><tr><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">mathjax</p></td><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">MathType</p></td></tr><tr><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">wordcount</p></td><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">word-count</p></td></tr><tr><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">Code Snippets</p></td><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">Code Blocks</p></td></tr><tr><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">scayt</p></td><td style="border:1px solid black;padding:5px;"><p style="margin-left:0px;">Proofreader</p></td></tr></tbody></table></figure>

<p style="margin-left:0px;">The most significant lift was migrating from <a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/docs/ckeditor4/latest/features/codesnippet.html">Code Snippets</a> to <a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/docs/ckeditor5/latest/features/code-blocks.html">Code Blocks</a>. CKEditor 5 has a much simpler integration for syntax highlighting. Instead of a &nbsp;<a target="_blank" rel="noopener noreferrer" href="https://prismjs.com/">Prism.js</a> plugin, I simply included Prism.js as a script in my templates. It works by choosing your languages from <a target="_blank" rel="noopener noreferrer" href="https://prismjs.com/download.html#themes=prism&amp;languages=markup+css+clike+javascript">Prism's download page</a> and then configuring Code Blocks to match that same set of languages. Prism doesn't just offer support for language syntax. It also includes support for git commands and Apache config files.</p>

<pre><code class="language-json">"codeBlock": {
    "languages": [
        {"language": "python", "label": "Python"},
        {"language": "css", "label": "CSS"},
        {"language": "yaml", "label": "YAML"},
        {"language": "json", "label": "JSON"},
        {"language": "git", "label": "Git"},
        {"language": "sql", "label": "SQL"},
        {"language": "html", "label": "HTML"},
        {"language": "bash", "label": "BASH"},
        {"language": "javascript", "label": "JavaScript"},
        {"language": "apacheconf", "label": "ApacheConf"},
    ]
}</code></pre>

<p style="margin-left:0px;">CKEditor 5's downside is that I can't see syntax highlighting while in edit mode.</p>

<blockquote><p style="margin-left:0px;"><i>Although live code block highlighting <strong>is impossible when editing</strong> in CKEditor 5 (</i><a target="_blank" rel="noopener noreferrer" href="https://github.com/ckeditor/ckeditor5/issues/436#issuecomment-548399675"><i>learn more</i></a><i>), the content can be highlighted when displayed in the frontend (e.g. in blog posts, messages, etc.).</i></p><p style="margin-left:0px;"><a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/docs/ckeditor5/latest/features/code-blocks.html#integration-with-code-highlighters"><i>Integrating with code highlighters</i></a></p><p style="margin-left:0px;"><i>- </i><a target="_blank" rel="noopener noreferrer" href="https://ckeditor.com/docs/ckeditor5/latest/features/code-blocks.html#integration-with-code-highlighters"><i>CKEditor Syntax Highlighting</i></a></p></blockquote>

<h2 style="margin-left:0px;">Image Uploads</h2>

<p style="margin-left:0px;">At first, I couldn't upload images. I got a 403 Forbidden response with a message about a missing CSRF token. Someone had&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/18">logged an issue</a>, and the <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/18#issuecomment-817617907">maintainer replied</a> he created the module to work on the admin page, not the front-end. After reading <a target="_blank" rel="noopener noreferrer" href="https://stackoverflow.com/questions/17507800/how-do-i-modify-the-file-upload-handlers-in-a-class-based-view-with-csrf-middlew">this stack overflow thread</a> and reviewing how <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/topics/http/file-uploads/">FileUpload works</a>, I solved it myself. I published my workaround in a <a target="_blank" rel="noopener noreferrer" href="https://app.prowritingaid.com/second%20issue">second issue</a>. Hope it gets resolved in the official module soon!</p>

<p style="margin-left:0px;">The second issue was that image uploads were not going into /media/uploads like the <a target="_blank" rel="noopener noreferrer" href="https://django-ckeditor.readthedocs.io/en/latest/">django-ckeditor</a> implementation. In CKEditor 4, you set the upload path using a variable in settings.py that specifies where you want the uploaded image to go. I logged <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/64">an enhancement</a> since I didn't know how to do it in django-ckeditor-5. The <a target="_blank" rel="noopener noreferrer" href="https://app.prowritingaid.com/he%20maintainer%20commented%20back">maintainer commented</a> that a custom storage class could control where CKEditor 5 uploads images. He also added a snippet on the <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5">home page of the repo</a> so others can benefit.</p>

<h2 style="margin-left:0px;">Inline Scripts and Styles</h2>

<p style="margin-left:0px;">When I removed unsafe-inline scripts from my CSP, there weren't any errors in the console as in CKEditor 5.! Unfortunately, it failed with inline styles. I logged <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/65">another issue,</a> and the <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/65#issuecomment-1140424863">maintainer replied</a> that it's not an issue with CKEditor 5 but with one or more of its plugins. It's up to me to either remove those plugins or <a target="_blank" rel="noopener noreferrer" href="https://content-security-policy.com/hash/">add hashes to my CSP</a> to accommodate them.</p>

<h2 style="margin-left:0px;">Form Field Widgets</h2>

<p style="margin-left:0px;">Another migration issue I ran into was that <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/forms/widgets/">form widgets</a> no longer work with text content fields. I <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/62">logged an issue</a>, and the <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5/issues/62#issuecomment-1140284738">maintainer replied</a> with a working example of how to fix it! Instead of <code>forms.Textarea,</code> I should use <code>CKEditor5Wigdet.</code>He even added the example to the <a target="_blank" rel="noopener noreferrer" href="https://github.com/hvlads/django-ckeditor-5">home page</a>. Hopefully, it helps others!</p>

<h2 style="margin-left:0px;">Conclusion</h2>

<p style="margin-left:0px;">Migrating from CKEditor 4 to CKEditor 5 was no easy feat, having to make several configuration changes to migrate plugins. I had issues with image uploads, form widgets, and inline styles. The good news is that CKEditor 5 allowed me to strengthen my CSP by removing unsafe-inline scripts. Blogthedata.com now has an <a target="_blank" rel="noopener noreferrer" href="https://observatory.mozilla.org/analyze/blogthedata.com">A+ in Mozilla Observatory</a>! Another benefit is that through my struggles, I helped improve the module. Over the next couple of weeks, I will use CKEditor 5 on production and fix any defects <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/pull/82">in the PR</a>.&nbsp;</p>
