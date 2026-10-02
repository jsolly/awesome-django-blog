---
slug: how-to-get-100-percent-unit-test-coverage
title: Achieving 100% Unit Test Coverage | A Step-by-Step Guide
category: dev-tools
description: Learn how to achieve 100% unit test coverage in your application with this step-by-step guide, covering route, view, model, form testing and more.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/unittest_coverage.png
legacyImage: post_metaimgs/unittest_coverage.png
imageAlt: A list of python files with 100% test coverage
imageAttribution: ""
imageWidth: 425
imageHeight: 272
published: "2022-04-08T03:03:14Z"
updated: "2022-04-08T03:03:14Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to achieve 100% unit test coverage in your application with this step-by-step guide, covering route, view, model, form testing and more.</p>
legacyId: 31
related:
  - two-weird-reasons-I-love-unit-tests
  - how-to-implement-content-security-policy-django
  - how-to-test-and-debug-django-templates
---

<a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/test-strategy-no-existing-tests/">I made a a commitment 12 days ago</a> to achieve 100% unit test coverage (starting at 0%). Promise, fulfilled!

Curious about unit testing your app?

The first step is to figure out where you stand with current test coverage. Python has an excellent library called <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/coverage/">coverage</a> that tells you how many statements your tests touch and what is missing. Output looks like this:

<img class="image_resized" style="height:569px;width:593px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220407221910-1.png" alt="Python Coverage report showing unit test coverage for each file.">

The lowest hanging fruit is ensuring routes hook up to the correct View. Here, I’m testing the home route links to the HomeView.

<pre><code class="language-python">def test_home_url_is_resolved(self):
    self.assertEqual(resolve(self.home_url).func.view_class, HomeView)</code></pre>

After testing routes, move on to Views. For basic Views, you check that a GET results in a 200 (OK) response and the response is using the correct HTML template.

<pre><code class="language-python">def test_post_detail_view(self):
        response = self.client.get(self.post1_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')</code></pre>

The next step is testing Models. We test objects can be created and any methods work as expected. In my case, a Comment associates to a single Post and author. On line 3, we check that the \_\_str\_\_ override method returns Comment content.

<pre><code class="language-python">def test_comment(self):
        test_comment = Comment.objects.create(post=self.post1, content="I am a comment", author=self.user1)
        self.assertEqual(str(test_comment), "I am a comment")
        self.assertEqual(test_comment.get_absolute_url(), self.post1_detail_url)</code></pre>

Moving on to Forms…Forms are the way Views structure data to be passed into Models, creating new objects. My Post object has 13 attributes. Some are user-provided (content, slug, snippet) whereas others internally generated (likes, views, date posted). 

<pre><code class="language-python">def test_post_form_valid_data(self):
        form = PostForm(data={
            "title": "My Second Post",
            "slug": "second-post",
            "category": "productivity",
            "metadesc": "I can make you more productive!",
            "draft": False,
            # "metaimg" : ""
            # "metaimg"_mimetype : ""
            "snippet": "Do the things",
            "content": "Do the things. All the things",
            # date_posted : ""
            "author": self.user1
            # "likes"
            # "views"

        })

        self.assertTrue(form.is_valid())</code></pre>

That’s it! My next step is to create integration and acceptance tests. Unlike unit testing, there's no 0-100%. You can write infinite amounts of integration and acceptance tests. 

Until next time!
