---
slug: Adding-views-likes-to-posts
title: Implementing Anonymous Likes and Views in Django - A Guide
category: web-dev
description: Learn to implement anonymous likes and views in Django with a step-by-step guide. Discover the best ways to track and record user engagement on your website.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/postModel.png
legacyImage: post_metaimgs/postModel.png
imageAlt: Screenshot of code for Post model
imageAttribution: ""
imageWidth: 1538
imageHeight: 832
published: "2021-12-31T05:59:46Z"
updated: "2021-12-31T05:59:46Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p style="text-align:start;">Learn to implement anonymous likes and views in Django with a step-by-step guide. Discover the best ways to track and record user engagement on your website.</p>
legacyId: 7
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - compress-minify-assets-69-percent-faster-page-load
  - UI-enhancement-leads-to-major-architecture-changes
---

This was one of the most fun features to implement. I came across a couple Youtube videos on how other's pulled this off. Namely, I stole from one of my favorite Youtubers, <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/watch?v=PXqRPqDjDgc">John Elder (Also known as Codemy.com)</a>. He had a good approach, but my beef with his implementation was that he tied it to the user model...meaning that you needed to be logged in to like posts. I wanted an anonymous like button. Did a little more searching and came across Youtuber, codepiep, who made a video about an <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/watch?v=AZwc9hDBi04">anonymous like button</a>. I liked his approach too, but I thought his code was quite verbose...plus his Django site was a lot different than mine in that he didn't have the same Post model I was using.

I implemented likes and views in a way that combined both of their approaches. The way it works is that every time someone visits one of my posts, I grab the IP address and throw it into an IP\_Person table. That way, it is 'semi-anonymous' in that I don't know who is viewing and liking my posts (Probably a bunch of bots)...but I can have persistent 'likes' because IP addresses are relatively consistent. Someone cannot keep liking the post over and over to drive the number upward.

Obtsining the client IP is actually pretty straightforward

<pre><code class="language-python">def get_client_ip(request):
&nbsp; &nbsp; x_forward_for = request.META.get("HTTP_X_FORWARD_FOR")
&nbsp; &nbsp; if x_forward_for:
&nbsp; &nbsp; &nbsp; &nbsp; ip = x_forward_for.split(",")[0]
&nbsp; &nbsp; else:
&nbsp; &nbsp; &nbsp; &nbsp; ip = request.META.get("REMOTE_ADDR")
&nbsp; &nbsp; return ip</code></pre>

There's a OnetoMany relationship between my IP\_Person table and the post\_views and post\_likes tables. A user will only get one record in the IP\_Person table, but they could like or view many posts.

<pre><code class="language-python">class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    content = RichTextUploadingField(blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, default='uncategorized')
    -&gt; likes = models.ManyToManyField(IpPerson, related_name="post_likes", blank=True)
    -&gt; views = models.ManyToManyField(IpPerson, related_name="post_views", blank=True)</code></pre>

Quite happy with how it all turned it!
