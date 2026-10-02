---
slug: migrating-portfolio-from-django-to-astro-js
title: "Django to Astro: Migrating a Django Portfolio to Astro.js"
category: web-dev
description: Learn about the the process of migrating a Django portfolio to Astro.js. From Django templates and views, to .astro components!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/DjangoToAstro.webp
legacyImage: post_metaimgs/DjangoToAstro.webp
imageAlt: Django logo with an arrow pointing to the Astro.js logo
imageAttribution: Built with Canva
imageWidth: 1280
imageHeight: 720
published: "2024-04-05T17:48:15.466Z"
updated: "2024-04-17T14:48:24.151Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Migrating from Django to Astro.js, I simplified my web development workflow by adopting Astro's efficient, JSX-like templating for my portfolio. This transition not only streamlined the development process but also led to substantial savings on hosting costs, demonstrating Astro.js's value as a modern web development framework.</p>
legacyId: 130
related:
  - three-scenarios-i-dont-use-tailwind
  - smartly-load-CSS-JS-page-load-time
  - how-to-add-social-share-buttons-to-your-website
---

## Motivation

In the quest for a more streamlined and efficient web development workflow, I journeyed from Django to Astro.js. My initial platform, blogthedata.com, served as both my blog and portfolio, but its cumbersome nature prompted me to consider separation, aiming for simplicity and speed.

Astro.js caught my attention for its unique approach to web development, blending the best of static site generation with server-side JavaScript. This framework's lack of a JavaScript runtime and its framework-agnostic nature were particularly appealing, aligning with my minimalist preferences. It promised a more straightforward, faster way to develop websites without sacrificing power or flexibility.

## Django to Astro.js Here I go!

The transition from Django to Astro.js was surprisingly smooth. Astro's server-side templating language shares similarities with JSX, making the adaptation process almost seamless. The challenge was to convert Django template code into Astro's equivalent, a task that proved less daunting than anticipated. Here’s how I transformed a Django carousel component into an Astro component:

<strong>Django Template Code</strong>

A traditional Django component for a carousel featuring loops and conditional rendering within the template.

<pre><code class="language-html">&lt;div class="testimonial-carousel"&gt;
  &lt;h2 class="testimonial-title" id="carouselExampleCaptions"&gt;Testimonials&lt;/h2&gt;
  &lt;div class="carousel-wrapper"&gt;
    &lt;div class="carousel-container"&gt;
      &lt;button class="carousel-control-prev" type="button" aria-label="Previous"&gt;&amp;#10094;&lt;/button&gt;
      &lt;div class="carousel-inner"&gt;
        {% for item in carousel_items %}
        &lt;div class="carousel-item {% if forloop.first %}active{% endif %}" data-index="{{ forloop.counter0 }}"&gt;
          &lt;div class="carousel-item-content"&gt;
            &lt;img class="avatar-img" src="{% static item.avatar_url %}" alt="avatar" /&gt;
            &lt;div class="carousel-content"&gt;
              &lt;div class="carousel-text"&gt;
                &lt;h3 class="carousel-name"&gt;{{ item.name }}&lt;/h3&gt;
                &lt;p class="carousel-position"&gt;{{ item.position }}&lt;/p&gt;
                &lt;p class="carousel-info"&gt;{{ item.company }} - {{ item.year }}&lt;/p&gt;
              &lt;/div&gt;
              &lt;p class="testimonial-quote"&gt;{{ item.quote }}&lt;/p&gt;
              &lt;p class="carousel-review-link"&gt;&lt;a target="_blank" rel="noopener noreferrer" href="{{ item.link }}"&gt;Open
                  review on LinkedIn&lt;/a&gt;&lt;/p&gt;
            &lt;/div&gt;
          &lt;/div&gt;
        &lt;/div&gt;
        {% endfor %}
      &lt;/div&gt;
      &lt;button class="carousel-control-next" type="button" aria-label="Next"&gt;&amp;#10095;&lt;/button&gt;
    &lt;/div&gt;
  &lt;/div&gt;
&lt;/div&gt;
&lt;!-- Indicators --&gt;
&lt;ol class="carousel-indicators"&gt;
  {% for item in carousel_items %}
  &lt;li {% if forloop.first %}class="active" {% endif %} data-carousel-index="{{ forloop.counter0 }}"&gt;&lt;/li&gt;
  {% endfor %}
&lt;/ol&gt;</code></pre>

I also needed to migrate code from the Django view that provided the data for the carousel elements.

<strong>Django View Code</strong>

<pre><code class="language-python">class PortfolioView(ListView):
    model = Post
    template_name = "blog/portfolio.html"  # &lt;app&gt;/&lt;model&gt;_&lt;viewtype&gt;.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.active().filter(category__slug="portfolio")

    def get_context_data(self, *args, **kwargs):
        carousel_items = [
            {
                "avatar_url": "portfolio/AmyBrazil.webp",
                "name": "Amy Brazil",
                "position": "Direct Manager",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "I had the pleasure to hire, onboard and manage John...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            # Additional Carousel Elements
        ]
        context = super().get_context_data(*args, **kwargs)
        context["carousel_items"] = carousel_items
        return context</code></pre>

Here is the final conversion of the template and view code combined into one .astro component. The conversion involved adapting Django's template syntax to Astro's JSX-like syntax, focusing on iterating over items and dynamically rendering components based on conditions.

<strong>.Astro component</strong>

<pre><code class="language-python">---
import { Image } from "astro:assets";
import AmyBrazilAvatar from "/src/images/AmyBrazil.webp";
import CraigUtleyAvatar from "/src/images/CraigUtley.webp";
import MeredithBeanAvatar from "/src/images/MeredithBean.webp";
import KathrynThorpeAvatar from "/src/images/KathrynThorpe.webp";
import TaylorOshanAvatar from "/src/images/TaylorOshan.svg";

const carouselItems = [
	{
		avatar: AmyBrazilAvatar,
		name: "Amy Brazil",
		position: "Direct Manager",
		company: "YellowfinBI",
		year: "2022",
		quote: "I'd hire him back in a heartbeat.",
	},
	// Aditional Carousel Items
];
---

&lt;script src="/src/scripts/carousel.js"&gt;&lt;/script&gt;

&lt;div class="text-center"&gt;
    &lt;h2
        class="text-3xl leading-none tracking-tight mb-3"
        id="carouselExampleCaptions"
    &gt;
        Testimonials
    &lt;/h2&gt;
    &lt;div class="relative"&gt;
        &lt;div class="flex items-center justify-center"&gt;
            &lt;button
                class="carousel-control-prev absolute left-14 top-1/2 transform -translate-y-1/2 text-4xl cursor-pointer"
                type="button"
                aria-label="Previous"&gt;&amp;#10094;&lt;/button
            &gt;
            &lt;div class="flex flex-col items-center"&gt;
                {
                    carouselItems.map((item, index) =&gt; (
                        &lt;div
                            class={`carousel-item ${
                                index === 0 ? "block" : "hidden"
                            } data-index=${index}`}
                        &gt;
                            &lt;div class="mb-3 flex flex-col items-center"&gt;
                                &lt;Image
                                    class="rounded-full shadow-lg mb-3 max-w-[150px] max-h-[150px]"
                                    src={item.avatar}
                                    alt="avatar"
                                    loading="eager"
                                /&gt;
                                &lt;div class="flex flex-col items-center gap-2 min-h-[160px]"&gt;
                                    &lt;div&gt;
                                        &lt;h3 class="font-normal font-xs leading-relaxed"&gt;
                                            {item.name}
                                        &lt;/h3&gt;
                                        &lt;p class="font-bold text-lg leading-none"&gt;
                                            {item.position}
                                        &lt;/p&gt;
                                        &lt;p class="text-xs leading-relaxed"&gt;
                                            {item.company} - {item.year}
                                        &lt;/p&gt;
                                    &lt;/div&gt;
                                    &lt;p class="testimonial-quote max-w-[450px] break-words text-xl"&gt;
                                        {item.quote}
                                    &lt;/p&gt;
                                &lt;/div&gt;
                            &lt;/div&gt;
                        &lt;/div&gt;
                    ))
                }
                &lt;!-- The # of indicators matches the # of carousel items --&gt;
                &lt;ol class="flex justify-center gap-2"&gt;
                    {
                        carouselItems.map((_, index) =&gt; (
                            // Initialize the first indicator as active on page load
                            &lt;li
                                class={`w-2.5 h-2.5 cursor-pointer transition-colors duration-300 ease-in-out ${
                                    index === 0 ? "bg-accent" : "bg-gray-300"
                                }`}
                                data-carousel-index={index}
                            /&gt;
                        ))
                    }
                &lt;/ol&gt;
            &lt;/div&gt;
            &lt;button
                class="carousel-control-next absolute right-14 top-1/2 transform -translate-y-1/2 text-4xl cursor-pointer"
                type="button"
                aria-label="Next"&gt;&amp;#10095;&lt;/button
            &gt;
        &lt;/div&gt;
    &lt;/div&gt;
&lt;/div&gt;</code></pre>

You can see that the syntax is very similar. Instead of injecting variables like this, \`<code>{{ item.position }}</code>you simply do it with a single curly brace, <code>{ item.position}</code>.

## Conclusion

Migrating to Astro.js from Django has been a revelation in web development simplicity and efficiency. The ease of integrating server-side and client-side logic in Astro components, combined with its impressive documentation, has made this transition a rewarding experience. For developers considering a shift to a more streamlined, statically-generated approach to web development, Astro.js offers a compelling pathway, echoing familiar paradigms while introducing powerful new capabilities.

Instead of running a server, my portfolio is hosted statically in S3. I'm paying a quarter a month to host and serve my site. That's a bargain!

Until next time!

## Reference

<a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/404">PR removing portfolio from Django Blog</a>

<a target="_blank" rel="noopener noreferrer" href="https://johnsolly.dev/">New Portfolio Page</a>

New Astro.js Github Repo
