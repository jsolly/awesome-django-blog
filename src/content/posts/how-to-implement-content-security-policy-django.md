---
slug: how-to-implement-content-security-policy-django
title: Improve Security With a Content Security Policy | A Step-By-Step Guide
category: web-dev
description: Implement Content Security Policy for website security and user protection, using features like nonces, hashes, and source lists.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/content_security_policy.png
legacyImage: post_metaimgs/content_security_policy.png
imageAlt: Screenshot of Content Security Policy directives
imageAttribution: ""
imageWidth: 1440
imageHeight: 754
published: "2022-05-24T22:22:56Z"
updated: "2024-11-06T13:41:08.074Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Implement Content Security Policy for website security and user protection, using features like nonces, hashes, and source lists.</p>
legacyId: 50
related:
  - migrating-to-django-4x
  - migrating-to-ckeditor-5
  - smartly-load-CSS-JS-page-load-time
---

<blockquote><p style="margin-left:0px;"><strong>Content Security Policy</strong>&nbsp;(<a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Glossary/CSP">CSP</a>) is an added layer of security that helps to detect and mitigate certain types of attacks, including Cross-Site Scripting (<a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Glossary/Cross-site_scripting">XSS</a>) and data injection attacks. These attacks are used for everything from data theft, to site defacement, to malware distribution.<br>- <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP">MDN</a></p></blockquote>

<p style="margin-left:0px;">Blogthedata.com now has a Content Security Policy and an <a target="_blank" rel="noopener noreferrer" href="https://observatory.mozilla.org/analyze/blogthedata.com">A+ rating on Mozilla Observatory</a>. The journey began early this month when I <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-a-perfect-mozilla-observatory-score/">got an F on Observatory’s security audit</a>. Since then, I’ve beefed up security, including <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-implement-subresource-integrity-django/">creating an SRI</a> and a CSP. W3C published the <a target="_blank" rel="noopener noreferrer" href="https://www.w3.org/TR/CSP/">latest CSP standard</a> on June 29th, 2021.</p>

<p style="margin-left:0px;">In Django, we implement a CSP using the <a target="_blank" rel="noopener noreferrer" href="https://django-csp.readthedocs.io/en/latest/">django-csp</a> module. After installation, you add CSP directives to your settings.py file.</p>

<pre><code class="language-python"># settings.py
# Content Security Policy
CSP_DEFAULT_SRC = ("'none'",)
CSP_STYLE_SRC = ("'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'")
CSP_SCRIPT_SRC = (
	"'self'",
	"https://cdn.jsdelivr.net",
)
CSP_IMG_SRC = ("'self'", "data:")
CSP_FONT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_SRC = ("*",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = ("'self'", "https://blogthedata.us14.list-manage.com")
CSP_OBJECT_SRC = ("'none'",)</code></pre>

<p style="margin-left:0px;"><strong>CSP_DEFAULT_SRC</strong> - The master directive. With a value of ‘none’ it’s saying ‘block everything unless it’s specifically allowed,’ It’s a good security practice because an allow list won’t block items you might have forgotten. Block everything by default and then selectively allow what you need.</p>

<p style="margin-left:0px;"><strong>CSP_STYLE_SRC</strong> - This tells Django where CSS may come from. In my case, I am allowing styles hosted on my server (self) and Bootstrap CSS, served through jsdeliver. I needed to include ‘unsafe-inline’ because a few plugins I use have inline styles. There’s an <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/issues/81">open issue</a> to resolve this one.</p>

<p style="margin-left:0px;"><strong>CSP_SCRIPT_SRC</strong> - Same as STYLE_SRC, but this concerns what’s inside a &lt;script&gt; tag.</p>

<p style="margin-left:0px;"><strong>CSP_IMG_SRC</strong> - I host site images locally, so I don’t need to allow external sites like Imgur. The downside to this directive is that it prevents me from having any images on my site hosted on another domain. I also added <code>data:</code> to allow CKEditor’s drag/drop image support, which <a target="_blank" rel="noopener noreferrer" href="https://github.com/ckeditor/ckeditor4/issues/4681">embeds the image as a base44 encoded string</a>. I could opt for regular image uploads only, but I kept this in for convenience.</p>

<p style="margin-left:0px;"><strong>CSP_FONT_SRC</strong> - Where fonts can come from.</p>

<p style="margin-left:0px;"><strong>CSP_CONNECT_SRC</strong> - Restricts URLs that load using script interfaces such as WebSocket and XMLHttpRequests.</p>

<p style="margin-left:0px;"><strong>CSP_FRAME_SRC</strong> - I used &nbsp;‘ * ‘ to wildcard all domains in a child iframe. I am not restricting myself from putting something inside &lt;iframe&gt; when the iframe lives on blogthedata.com. This contrasts with SRC_FRAME_ANCESTORS, which dictates which domains can put blogthedata.com into an iframe.</p>

<p style="margin-left:0px;"><strong>CSP_BASE_URI</strong> - The &lt;base&gt; tag specifies the target of relative URLs in a site.</p>

<p style="margin-left:0px;"><strong>CSP_FORM_ACTION</strong> - Where &lt;form&gt; can submit. Most of my forms POST to routes within my application, except the&nbsp;Mailchimp newsletter sign-up which uses .us14.list-manage.com</p>

<p style="margin-left:0px;"><strong>CSP_OBJECT_SRC</strong> - Limts what sources for &lt;object&gt;, &lt;embed&gt;, and &lt;applet&gt; tags.</p>

<h2 style="margin-left:0px;">My Approach and Gotchas Encountered&nbsp;</h2>

<p style="margin-left:0px;">I&nbsp;first set <strong>CSP_DEFAULT_SRC </strong>to ‘none’ (block everything) and began visiting pages and running unit tests. My first issue was that CKEditor 4 bundles inline CSS with JavaScript in the ckeditor.js file. CSP policies restrict inline &lt;style&gt; and &lt;script&gt; tags. CKEditor improved CSP support in version 5, so I decided to migrate. You can read more about it <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/migrating-to-ckeditor-5/">in this blog post</a>.</p>

<h2 style="margin-left:0px;">Social Share embedded Scripts and Styles</h2>

<p style="margin-left:0px;">Most social share buttons provided by companies such as <a target="_blank" rel="noopener noreferrer" href="https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/plugins/share-plugin">LinkedIn</a> and <a target="_blank" rel="noopener noreferrer" href="https://publish.twitter.com/?buttonType=TweetButton&amp;widget=Button">Twitter</a> have embedded scripts and styles. I worked my way around that and wrote on it in <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-add-social-share-buttons-to-your-website/">this post</a>.</p>

<h2 style="margin-left:0px;">Kofi Donate Button and Mailchimp Embed Form had inline styles and scripts</h2>

<p style="margin-left:0px;">I had to reverse engineer HTML templates, so Kofi and Mailchimp did not violate the CSP. This involved hosting the JavaScript locally and moving inline styles into a separate CSS file. The changes are in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/80/files">this PR</a>.</p>

<h2 style="margin-left:0px;">Broken styling on the sitemap page</h2>

<p style="margin-left:0px;">Another interesting issue I ran into was that I broke inline styles on the sitemap page. I don’t think it’s a problem because this page doesn’t need styling. The only reason I have a sitemap page is for <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/help-google-spider-with-sitemaps-and-robots-file/">site spiders to understand my site better</a>. I came across this <a target="_blank" rel="noopener noreferrer" href="https://www.reddit.com/r/django/comments/i9mo5o/sitemapxml_and_robotstxt_content_security_policy/">Reddit thread</a> that confirmed my thoughts. CSPs are for protecting users on your site, not robots.</p>

<h2 style="margin-left:0px;">Conclusion</h2>

<p style="margin-left:0px;">Implementing a CSP added XSS protection to blogthedata.com besides increasing the site’s score on Mozilla Observatory. I ran into many setbacks, but they were surmounted. Consider adding a CSP to your site to make it more secure.</p>
