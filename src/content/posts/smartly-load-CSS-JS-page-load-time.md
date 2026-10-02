---
slug: smartly-load-CSS-JS-page-load-time
title: Optimize Render Blocking Resources With Template Blocks in Django
category: web-dev
description: Learn how to optimize your website's page load speed with template blocks and a Google Lighthouse audit. Discover how to remove unnecessary CSS and JavaScript.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/render_blocking_resources.png
legacyImage: post_metaimgs/render_blocking_resources.png
imageAlt: A <head> snippet with a big X covering it
imageAttribution: ""
imageWidth: 816
imageHeight: 495
published: "2022-04-09T03:02:19Z"
updated: "2022-04-09T03:02:19Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to optimize your website's page load speed with template blocks and a Google Lighthouse audit. Discover how to remove unnecessary CSS and JavaScript.</p>
legacyId: 33
related:
  - how-to-implement-subresource-integrity-django
  - how-to-add-leaflet-js-maps-inside-a-django-site
  - migrating-portfolio-from-django-to-astro-js
---

A <a target="_blank" rel="noopener noreferrer" href="https://developers.google.com/web/tools/lighthouse/">Google Lighthouse</a> audit showed several <a target="_blank" rel="noopener noreferrer" href="https://developers.google.com/publisher-ads-audits/reference/audits/ad-render-blocking-resources">render blocking</a> resources slowing down the page. Anything in a GL audit about 'unneeded JS/CSS' or excessive render blocking resources is a red flag.

Turns out each page was pulling in unused JS/CSS because of inheritance from the base.html template. Here's a snippet of the home route's head tag.

<pre><code class="language-python language-markup">&lt;head&gt;
    &lt;!-- ckeditor --&gt;
    &lt;link href="{% static 'ckeditor/ckeditor/plugins/prism/lib/prism/prism_patched.min.css' %}" rel="stylesheet"&gt;
    &lt;script src="{% static 'ckeditor/ckeditor/plugins/prism/lib/prism/prism_patched.min.js' %}"&gt;&lt;/script&gt;

    &lt;!-- MathJax--&gt;
    &lt;script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML"&gt;&lt;/script&gt;

  &lt;!-- Bootstrap --&gt;
  &lt;link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
    integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous"&gt;
  &lt;script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
    crossorigin="anonymous"&gt;&lt;/script&gt;

  &lt;!-- MailChimp--&gt;
  &lt;link href="//cdn-images.mailchimp.com/embedcode/classic-10_7_dtp.css" rel="stylesheet" type="text/css"&gt;

    &lt;!-- My CSS --&gt;
    &lt;link rel="stylesheet" type="text/css" href="{% static 'main.css' %}" /&gt;
&lt;/head&gt;</code></pre>

Many imports are not leveraged at all!! For example, the ckeditor and MathJax CSS/JS only kick in when viewing individual posts or creating new ones.

One solution is to only use these libraries on pages that need them. In Django, you accomplish this by including a template block within the head tag. By using these blocks on pages inheriting the base template, you add resources to the \<head\> on a page-by-page basis.

I also made the Mailchimp CSS script async because it is only used by the newsletter component. I am OKAY with taking longer to become interactive.

The \<head\> in the base.html shrunk and the home route load time dropped by a second!

<pre><code class="language-python language-markup">&lt;head&gt;
  {% block head %}

  {% endblock %}

  &lt;!-- Bootstrap --&gt;
  &lt;link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
    integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous"&gt;
  &lt;script async src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"
    integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p"
    crossorigin="anonymous"&gt;&lt;/script&gt;

  &lt;!-- MailChimp--&gt;
  &lt;link href="//cdn-images.mailchimp.com/embedcode/classic-10_7_dtp.css" rel="stylesheet" type="text/css" media="print"
    onload="this.media='all'"&gt;

  &lt;!-- My CSS --&gt;
  &lt;link rel="stylesheet" type="text/css" href="{% static 'main.css' %}" /&gt;
&lt;/head&gt;</code></pre>

On line 9, I add an async tag to the bootstrap JS. This increases time to be interactive, but I haven't noticed an impact other than <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Glossary/First_contentful_paint">FCP dropping</a> (that's a good thing). For CSS, I used <a target="_blank" rel="noopener noreferrer" href="https://stackoverflow.com/questions/32759272/how-to-load-css-asynchronously/46750893#46750893"> this hacky approach</a> on SO which involves adding two attributes to the script tag to remove it from being a render blocking resource. See line 14 and 15.

For the post detail route where the user is seeing a full post, I use the {% block head %} to pull in the needed ckeditor and MathJax libraries.

<pre><code class="language-python language-markup">{% block head %}
    &lt;!-- MathJax--&gt;
    &lt;script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-AMS_HTML"&gt;&lt;/script&gt;

    &lt;!-- ckeditor --&gt;
    &lt;link href="{% static 'ckeditor/ckeditor/plugins/prism/lib/prism/prism_patched.min.css' %}" rel="stylesheet"&gt;
    &lt;script src="{% static 'ckeditor/ckeditor/plugins/prism/lib/prism/prism_patched.min.js' %}"&gt;&lt;/script&gt;
{% endblock %}</code></pre>

This way, the resources for the page becomes all the CSS/JS from the base.html plus whatever is placed inside the block.

Most websites can receive a performance boost by being smart about when and where JS/CSS loads. Check your site, today!
