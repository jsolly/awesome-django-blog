---
slug: how-to-add-social-share-buttons-to-your-website
title: Add Social Share Buttons to Your Blog Posts With OpenGraph Tags
category: web-dev
description: Add social share buttons to your blog posts with Twitter, LinkedIn, and Reddit. Get post previews to show correctly with Twitter meta tags and OpenGraph tags.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/social_networks.jpg
legacyImage: post_metaimgs/social_networks.jpg
imageAlt: Various social media icons. Facebook, Instagram, etc.
imageAttribution: https://2.bp.blogspot.com/-M-cVD8tA92k/XIlwhZ_Z-sI/AAAAAAAAPGE/RnV4x1RwTR0FWMef518GGi9aaRmgbLmxgCLcBGAs/s1600/Come-funzionano-i-social-network-1.jpg
imageWidth: 1200
imageHeight: 627
published: "2022-05-27T13:04:55Z"
updated: "2022-05-27T13:04:55Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Add social share buttons to your blog posts with Twitter, LinkedIn, and Reddit. Get post previews to show correctly with Twitter meta tags and OpenGraph tags.</p>
legacyId: 53
related:
  - migrating-to-django-4x
  - smartly-load-CSS-JS-page-load-time
  - why-I-stopped-using-pip-freeze
---

<p style="margin-left:0px;">You can now share posts on Twitter, LinkedIn, and Reddit!</p>

<p style="margin-left:0px;">I started working with a module called <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/django-social-share/">django-social-share</a>, but realized I could code it myself without an added dependency.</p>

<h2 style="margin-left:0px;">Twitter</h2>

<p style="margin-left:0px;">I began using code from the <a target="_blank" rel="noopener noreferrer" href="https://publish.twitter.com/?buttonType=TweetButton&amp;widget=Button">official Twitter share button page. It</a> didn’t work for me because it includes inline styles and scripts, invalidating my content security policy. Instead, I used <a target="_blank" rel="noopener noreferrer" href="https://sharingbuttons.io">sharingbuttons.io</a> which provides ‘JavaScript-less’ social share buttons. After adding the button, I also needed to include Twitter’s meta tags.</p>

<p style="margin-left:0px;">I won’t go through the Twitter meta tags since they are well-documented on <a target="_blank" rel="noopener noreferrer" href="https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/markup">Twitter’s card overview</a>. &nbsp;Twitter's tags are meant to augment Open Graph tags which <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/social-media-share-links-open-graph/">implemented last month</a>. For example, <code>"twitter:card"</code> has no complement in OG, but <code>title</code> does.</p>

<blockquote><p style="margin-left:0px;">Twitter card tags look similar to Open Graph tags, and are based on the same conventions as the Open Graph protocol. When using Open Graph protocol to describe data on a page, it is easy to generate a Twitter card without duplicating tags and data. When the Twitter card processor looks for tags on a page, it first checks for the Twitter-specific property, and if not present, falls back to the supported Open Graph property. This allows for both to be defined on the page independently, and minimizes the amount of duplicate markup required to describe content and experience.</p><p style="margin-left:0px;"><a target="_blank" rel="noopener noreferrer" href="https://developer.twitter.com/en/docs/twitter-for-websites/cards/guides/getting-started">Twitter docs</a></p></blockquote>

<p style="margin-left:0px;">I wasn't able to get my post's meta description to show up unless I added Twitter's tag for it. Twitter was also failing to pick up the image url when it was relative (/media/meta_imgs) so I needed to add a duplicate metaimg url tag specifically for Twitter.</p>

<pre><code class="language-html">{% block meta %}
&lt;!-- OpenGraph Tags --&gt;
&lt;meta name="description" content="{{ post.metadesc }}"&gt;
&lt;meta property="og:type" content="article"&gt;
&lt;meta property="article:published_time" content="{{ post.date_posted|date:’c’ }}"&gt;
&lt;meta name="author" content="{{ post.author.first_name }} {{ post.author.last_name }}"&gt;
&lt;meta property="og:image" content="{{ post.metaimg.url }}"&gt;
&lt;meta property="og:image:type" content="{{ post.metaimg_mimetype }}"&gt;
&lt;meta property="og:image:width" content="{{ post.metaimg.width }}"&gt;
&lt;meta property="og:image:height" content="{{ post.metaimg.height }}"&gt;
&lt;!-- Twitter Cards Meta Tags --&gt;
&lt;meta name="twitter:card" content="summary_large_image"&gt;
&lt;meta name="twitter:site" content="@_jsolly"&gt;
&lt;meta name="twitter:description" content="{{ post.metadesc }}"&gt;
&lt;meta name="twitter:image" content="{{ request.scheme }}://{{ request.get_host }}{{ post.metaimg.url }}"&gt;
{% endblock meta %}</code></pre>

<p style="margin-left:0px;">After adding everything to your template, you can test sharing with the <a target="_blank" rel="noopener noreferrer" href="https://cards-dev.twitter.com/validator">Twitter Card Validator</a>. It shows you a preview of your tweet before you post it.</p>

<h2 style="margin-left:0px;">LinkedIn</h2>

<p style="margin-left:0px;">This was straightforward since I had done most of the heavy lifting of adding OpenGraph tags, which I wrote about in <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/social-media-share-links-open-graph/">this post</a>. After adding the LinkedIn button on <a target="_blank" rel="noopener noreferrer" href="https://sharingbuttons.io">sharingbuttons.io</a>, it ‘just worked.’</p>

<h2 style="margin-left:0px;">Reddit</h2>

<p style="margin-left:0px;">I just added the button! Here’s a typical sharingbuttons.io button:</p>

<pre><code class="language-html">  &lt;!-- Sharingbutton Reddit --&gt;
    &lt;a class="resp-sharing-button__link" href="https://reddit.com/submit/?url={{ request.build_absolute_uri }}&amp;amp;resubmit=true&amp;amp;title={{ post.title }}" target="_blank" rel="noopener" aria-label="Share on Reddit"&gt;
      &lt;div class="resp-sharing-button resp-sharing-button--reddit resp-sharing-button--large"&gt;&lt;div aria-hidden="true" class="resp-sharing-button__icon resp-sharing-button__icon--solidcircle"&gt;
        &lt;svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"&gt;&lt;circle cx="9.391" cy="13.392" r=".978"/&gt;&lt;path d="M14.057 15.814c-1.14.66-2.987.655-4.122-.004-.238-.138-.545-.058-.684.182-.13.24-.05.545.19.685.72.417 1.63.646 2.568.646.93 0 1.84-.228 2.558-.642.24-.13.32-.44.185-.68-.14-.24-.445-.32-.683-.18zM5 12.086c0 .41.23.78.568.978.27-.662.735-1.264 1.353-1.774-.2-.207-.48-.334-.79-.334-.62 0-1.13.507-1.13 1.13z"/&gt;&lt;path d="M12 0C5.383 0 0 5.383 0 12s5.383 12 12 12 12-5.383 12-12S18.617 0 12 0zm6.673 14.055c.01.104.022.208.022.314 0 2.61-3.004 4.73-6.695 4.73s-6.695-2.126-6.695-4.74c0-.105.013-.21.022-.313C4.537 13.73 4 12.97 4 12.08c0-1.173.956-2.13 2.13-2.13.63 0 1.218.29 1.618.757 1.04-.607 2.345-.99 3.77-1.063.057-.803.308-2.33 1.388-2.95.633-.366 1.417-.323 2.322.085.302-.81 1.076-1.397 1.99-1.397 1.174 0 2.13.96 2.13 2.13 0 1.177-.956 2.133-2.13 2.133-1.065 0-1.942-.79-2.098-1.81-.734-.4-1.315-.506-1.716-.276-.6.346-.818 1.395-.88 2.087 1.407.08 2.697.46 3.728 1.065.4-.468.987-.756 1.617-.756 1.17 0 2.13.953 2.13 2.13 0 .89-.54 1.65-1.33 1.97z"/&gt;&lt;circle cx="14.609" cy="13.391" r=".978"/&gt;&lt;path d="M17.87 10.956c-.302 0-.583.128-.79.334.616.51 1.082 1.112 1.352 1.774.34-.197.568-.566.568-.978 0-.623-.507-1.13-1.13-1.13z"/&gt;&lt;/svg&gt;
      &lt;/div&gt;Share on Reddit&lt;/div&gt;
    &lt;/a&gt;</code></pre>

<h2 style="margin-left:0px;">Conclusion</h2>

<p style="margin-left:0px;">A clean implementation of social share buttons was challenging because most approaches violated my <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-implement-content-security-policy-django/">CSP (Content Security Policy). </a>Existing python modules were too heavy-handed, and official share buttons included inline styles and scripts. I settled on buttons created on <a target="_blank" rel="noopener noreferrer" href="https://sharingbuttons.io">sharingbuttons.io</a> and added Twitter meta tags, so my post previews show correctly on Twitter Cards. Try the buttons below, and let me know how they work!</p>
