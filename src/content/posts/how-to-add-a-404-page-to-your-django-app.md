---
slug: how-to-add-a-404-page-to-your-django-app
title: "Creating a Custom 404 Page in Django: A Step-by-Step Guide"
category: web-dev
description: "Create a custom 404 page in Django: Follow this step-by-step guide with code examples to create an eye-catching 404 page."
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/404_page.png
legacyImage: post_metaimgs/404_page.png
imageAlt: 404 page with a scarecrow and and a 'back to homepage' button
imageAttribution: ""
imageWidth: 1920
imageHeight: 885
published: "2022-07-02T17:33:46.863Z"
updated: "2022-07-02T17:33:46.863Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>Create a custom 404 page in Django: Follow this step-by-step guide with code examples to create an eye-catching 404 page.</p>"
legacyId: 71
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - how-to-get-100-percent-unit-test-coverage
  - admin-honeypot-page-to-catch-hackers
---

I was watching an excellent LinkedIn learning course, <a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/learning-login/share?account=42290089&amp;forceAccount=false&amp;redirect=https%3A%2F%2Fwww.linkedin.com%2Flearning%2Fadvanced-django%3Ftrk%3Dshare_ent_url%26shareId%3DMLA9EnspTR23PH%252B%252BTGsVfA%253D%253D">Advanced Django</a>, when I came across an example where the author talked about setting up a 404 page. 

I implemented it on blogthedata.com with <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/commit/f3364ac7eb3b2375ce1cf56f9de2a9c0b7c8838f">this commit</a>. Go ahead, try it out!

https://blogthedata.com/doesnotexist

I first needed to adjust my views so that if a post/category was not found, it threw a 404 error instead of a 500.

<pre><code class="language-python"># views.py
from django.shortcuts import get_object_or_404
def get_queryset(self):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])</code></pre>

The second was to add a 404 handler to my view. This references a template containing all HTML shown when a 404 is thrown. I thought it would be fun to search '404 page' within public Github repositories, and I was not disappointed! I came across <a target="_blank" rel="noopener noreferrer" href="https://github.com/OnlyManu/404-not-found-master">this one</a> which appears to be the result of a coding challenge where they were tasked to create a 404 page.

<pre><code class="language-python"># views.py
def handler_404(request, exception):
    return render(request, "blog/404_page.html")</code></pre>

Finally, add the handler to urls.py

<pre><code class="language-python"># urls.py
handler404 = "django_project.views.handler_404"</code></pre>

We now have a pretty 404 page instead of an ugly default page. If I want to go further, I could design templates and handlers for other types of errors, such as 500 (server error) and 403 (Not allowed). Perhaps I'll tackle that in the future!
