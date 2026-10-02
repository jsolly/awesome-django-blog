---
slug: adding-global-search
title: Searching for Answers - Implementing Search Functionality to the Site
category: web-dev
description: Learn to implement search functionality on your website with this guide, including using the 'Q' function to search titles and content of posts.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/globalSearch.png
legacyImage: post_metaimgs/globalSearch.png
imageAlt: Python code for global search
imageAttribution: ""
imageWidth: 1310
imageHeight: 708
published: "2022-01-12T15:52:32Z"
updated: "2022-01-12T15:52:32Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p style="text-align:start;">Learn to implement search functionality on your website with this guide, including using the 'Q' function to search titles and content of posts.</p>
legacyId: 10
related:
  - optimizing-ahrefs-orphan-pages-duplicate-content
  - help-google-spider-with-sitemaps-and-robots-file
  - Adding-views-likes-to-posts
---

Excited to implement search functionality to the site. This will be helpful in the future when there are a lot more posts and anyone wants to find posts that contain specific content.

I first grabbed a search toolbar from the <a target="_blank" rel="noopener noreferrer" href="https://getbootstrap.com/docs/5.1/components/navbar/">bootstrap website</a> which basically entailed looking through the navbars and yanking out the search functionality. When I initially implemented the navbar, I actually removed the default search because I wasn't ready to work on it, so I guess I am just putting it back!

Next up was wiring up the search button to make a POST request to the 'blog-search' url. Once it hit urls.py, the request is sent to the SearchView which does most of the work.

Found a useful <a target="_blank" rel="noopener noreferrer" href="https://youtu.be/AGtae4L5BbI?list=PLCC34OHNcOtqW9BJmgQPPzUpJ8hl49AGy">Youtube Video</a> for creating search functionality, but it's limited in that you can only search one field in the Post model. I wanted users to search both the title of a post AND the content of the post. The final view looked like this:

<pre><code class="language-python">def SearchView(request):
    """Controls what is shown to a user when they search for a post."""
    cat_list = Category.objects.all()
    if request.method == 'POST':
        searched = request.POST['searched']
        filtered_posts = Post.objects.filter(Q(content__icontains=searched) | Q(title__icontains=searched))
        return render(
            request,
            "blog/search_posts.html",
            {"cat_list": cat_list, "searched": searched, "filtered_posts": filtered_posts},
        )
    else:
        return render(
            request,
            "blog/search_posts.html",
            {"cat_list": cat_list},
        )</code></pre>

One line 194 you can see the implementation from the Youtube Video, but I went a step further. After reviewing the <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/3.2/topics/db/queries/">ckeditor docs</a>, I came across functionality called 'Q' which allows you to manufacture more complex queries. You can accomplish the equivalent of an 'OR' in SQL using the pipe character. In my case, it is searching and returning posts that contain the search query in either the content of the post OR the post's title.

I might look into adding more search functionality (like a date filter or searching Comment text)...but I am pretty happy with how it works for now.
