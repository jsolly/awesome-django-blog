---
slug: help-google-spider-with-sitemaps-and-robots-file
title: Improve SEO With a Sitemap.xml & Robots.txt - A Guide
category: web-dev
description: Learn how to improve your website's SEO with a sitemap.xml and robots.txt file. A step-by-step guide on how to create and use these files to boost SEO.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/spider.png
legacyImage: post_metaimgs/spider.png
imageAlt: A black widow spider
imageAttribution: ""
imageWidth: 2400
imageHeight: 1569
published: "2022-05-05T12:38:00Z"
updated: "2022-05-05T12:38:00Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to improve your website's SEO with a sitemap.xml and robots.txt file. A step-by-step guide on how to create and use these files to boost SEO.</p>
legacyId: 38
related:
  - security-txt-allows-researches-to-contact-you
  - optimizing-ahrefs-orphan-pages-duplicate-content
  - Adding-views-likes-to-posts
---

Yesterday, I posted <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-a-perfect-mozilla-observatory-score/">how to get an A+ in Mozilla's Observator security audit tool</a>. The security auditing tools also revealed my site was missing a robots.txt file. With <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/pull/44/files">this PR</a>, a proper robots.txt file is added to blogthedata.com!

The robots.txt file tells website spiders (also known as crawlers) which pages they may visit. It further communicates which urls are relevant and how often they update. I initially thought spiders were bad, but it’s more accurate to say that some spiders are naughty and some are nice. I guess that's true in real life, too!

One important spider to be aware of is <a target="_blank" rel="noopener noreferrer" href="https://developers.google.com/search/docs/advanced/crawling/googlebot">Googlebot</a>. If Googlebot never makes it to your website, you won't show up in Google search results AT ALL! Check this <a target="_blank" rel="noopener noreferrer" href="https://developers.google.com/search/docs/advanced/guidelines/how-search-works">Google article</a> for more info on how spiders are so important for Google Search.

Spiders will look for the following within a robots.txt file:

1 - Your web application's site map

2 - Directives on allowed/disallowed routes

So what is a sitemap, anyway?

<blockquote><p>A&nbsp;<strong>site map</strong>&nbsp;or&nbsp;<strong>sitemap</strong>&nbsp;is a list of pages of a web site.</p><p>Structured listings of a site's page help with&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Glossary/SEO">search engine optimization</a>, providing a link for web crawlers such as search engines to follow. Site maps also help users with site navigation by providing an overview of a site's content in a single glance.</p><p>- <a target="_blank" rel="noopener noreferrer" href="https://developer.mozilla.org/en-US/docs/Glossary/Site_map">MDN</a></p></blockquote>

Django includes site maps as out of the box functionality. Here’s <a target="_blank" rel="noopener noreferrer" href="https://ordinarycoders.com/blog/article/django-sitemap">a great tutorial</a> on implementing site maps in a Django app. For blogthedata.com, I added the following site maps:

\- The About Page

\- The Roadmap Page

\- All Post URLs

Here is a snippet of my PostSiteMap.

<pre><code class="language-python">class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.date_posted

    #def location() Django uses get_absolute_url() by default, so no need to define the location</code></pre>

The changefreq tells spiders how often to check the content for updates. My current implementation is not perfect because every post has a change frequency of 'weekly' when, in reality, posts do not modify once published.

A future enhancement might be to add my category pages (/site\_updates, /life\_advice) to the site map since they regularly update with new posts.

The priority property tells the spider how important the content is to a visitor. Not all pages are created equal!

You should have separate site maps for different pages because not every route updates as frequently. My about page, for example, has a change frequency of 'Monthly.'

<pre><code class="language-python">class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['blog-about']

    def location(self, item):
        return reverse(item)</code></pre>

After adding my sitemap, I went into <a target="_blank" rel="noopener noreferrer" href="https://search.google.com/search-console">Google Search Console</a> and submitted my sitemap url. Google successfully parsed my sitemap and found 33 paths! That should be all of my current blog posts + /about and /roadmap!

<img class="image_resized" style="height:344px;width:800px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220507054336-1.png" alt="Google sitemap page showing https://blogthedata.com/sitemap.xml having 33 routes detected">

After adding site maps for all the relevant pages, you'll want to incorporate this into a robots.txt file. You can see <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/robots.txt">my robots file here</a>. I include the sitemap url so the spider knows where to go to learn more about blogthedata.com

The second portion of the robots.txt file is including directives instructing spiders which pages are 'off limits.' I've included a single route, /admin. This is the page I used to administer my site and I would rather it not get indexed and show up in Google search!!

In conclusion, having a sitemap.xml + robots.txt file is important for making sure your site gets indexed by crawlers such as the Googlebot. It tells the spiders which pages you want to turn up in search results as well as how often pages update.

Add this functionality to improve your SEO! 🕷
