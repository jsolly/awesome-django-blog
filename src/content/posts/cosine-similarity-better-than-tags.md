---
slug: cosine-similarity-better-than-tags
title: Why Cosine Similarity Beats Tags for Blog Organization
category: web-dev
description: Discover how to improve blog organization by using LLMs and similarity scores instead of tags. Enhance user experience with automated related posts.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/relatedblogposts.webp
legacyImage: post_metaimgs/relatedblogposts.webp
imageAlt: Clean and modern blog page interface displaying a main blog post in the center with a large title, image, and a snippet of content. On the right side, there is a sidebar listing related posts with smaller images, titles, and brief descriptions. The design is minimalistic with a white background, black text, and accent colors like blue and green for highlights, making it visually appealing and easy to navigate.
imageAttribution: Dalle3
imageWidth: 1792
imageHeight: 1024
published: "2024-06-12T13:21:57.107Z"
updated: "2024-07-04T19:48:48.365Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Organizing blog posts efficiently is crucial for enhancing user experience and ensuring readers can easily find related content. Traditionally, this has been achieved through tagging systems. In this post, I explore an alternative approach that leverages large language models and similarity scores to automate finding and displaying related posts, eliminating the need for traditional tagging.</p>
legacyId: 132
related:
  - Adding-views-likes-to-posts
  - UI-enhancement-leads-to-major-architecture-changes
  - how-to-add-social-share-buttons-to-your-website
---

## Cosine Similarity \> Tags

Organizing blog posts efficiently is crucial for enhancing user experience and ensuring readers can easily find related content. Traditionally, this has been achieved through tagging systems, where each post is assigned relevant tags that users can click to find related posts. While this method is simple and easy to implement, it comes with its own set of challenges. Tags can often be too broad or too narrow, and managing them effectively can become cumbersome. In this blog post, I explore an alternative approach that leverages large language models and similarity scores to automate finding and displaying related posts, eliminating the need for traditional tagging.

## Why Tags Suck

My two gripes with tags are that it's hard to develop good tags that effectively separate posts. If I create a 'productivity' category, it might be too broad (too many posts are tagged) or too narrow (not enough posts are tagged). It's also a nightmare figuring out how many tags I should have and which ones should be attached to new posts.

I wanted to eliminate tags entirely and rely on a combination of large categories and something intelligent enough to determine which blog posts were related. This would allow me to do this automatically without any extra overhead.

Large language models had just started gaining popularity, and the RAG workflow closely resembled what I had sought. I wanted to know which posts were more related than others and use the similarity score to rank them.

## Moving Beyond Tags

The workflow I came up with compares each of my blog posts to every other post. This runs in O(n²) time, but since I only have 100 blog posts, it's not a big deal.

Here's how I did it:

## Step 1 - Create a Django Class for keeping track of the post similarities

<pre><code class="language-python">class Similarity(models.Model):
    	post1 = models.ForeignKey(
        	Post, related_name="similarities1", on_delete=models.CASCADE
    	)
    	post2 = models.ForeignKey(
        	Post, related_name="similarities2", on_delete=models.CASCADE
    	)
    	score = models.FloatField()
    	# Ensure that the same pair of posts can't be added twice
    	class Meta:
        	constraints = [
            	models.UniqueConstraint(fields=["post1", "post2"], name="unique_pair")
        	]</code></pre>

Each instance of Similarity is a unique pair of blog posts. If you had four blog with ids, 1, 2, 3, 4, the similarity table would look something like this:

<figure class="table"><table><thead><tr><th>id</th><th>post1_id</th><th>post2_id</th><th>score</th></tr></thead><tbody><tr><td>1</td><td>101</td><td>102</td><td>0.85</td></tr><tr><td>2</td><td>101</td><td>103</td><td>0.75</td></tr><tr><td>3</td><td>102</td><td>104</td><td>0.92</td></tr><tr><td>4</td><td>103</td><td>104</td><td>0.60</td></tr></tbody></table></figure>

When viewing the post detail page for any one post, a function runs to fetch the top three posts that are most similar to the current post

<pre><code class="language-python">    def get_related_posts(self) -&gt; models.QuerySet:
        """
        Get the top 3 related posts based on the cosine similarities.
        """
        return Post.objects.filter(
            id__in=self.similarities1.order_by("-score").values_list(
                "post2", flat=True
            )[:3]
        )</code></pre>

When a post is saved, a signal in signals.py listens for the post-created event. It recalculates all the similarities since the newly saved post could relate to existing posts. Again, this would not scale, but with 100 posts, it runs in less than a second.

<pre><code class="language-python">@receiver(post_save, sender=Post)
	def trigger_similarity_computation(sender, instance, **kwargs):
    	compute_similarity(instance.id)</code></pre>

<code>compute_simularity</code> is a pretty complex function, but the gist of it is that every post is compared pairwise to every other post using <a target="_blank" rel="noopener noreferrer" href="https://en.wikipedia.org/wiki/Cosine_similarity">Cosine Similarity</a>. If there are 100 posts, each post will have 99 cosine similarities. If you want to see the complete implementation, check out <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog">awesome-django-blog</a> on GitHub!

## Conclusion

Implementing an automated system to determine related blog posts based on similarity scores can significantly streamline content organization and improve user experience. We can ensure that readers are always presented with the most relevant content by utilizing a Django model to track post similarities and recalculating these scores whenever a new post is added. Although this approach may not scale well for larger blogs, it is highly effective for smaller sites with a manageable number of posts. This method reduces the overhead associated with manual tagging and provides a more intuitive and dynamic way to connect related content.
