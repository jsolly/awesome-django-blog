---
slug: three-scenarios-i-dont-use-tailwind
title: I Use TailwindCSS Except in These Three Scenarios
category: web-dev
description: Discover the benefits of using TailwindCSS for quick application development and learn why scoped CSS is a superior solution for many use cases.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/TailwindLogo.webp
legacyImage: post_metaimgs/TailwindLogo.webp
imageAlt: Tailwind Logo
imageAttribution: https://codekitapp.com/images/help/free-tailwind-icon@2x.png
imageWidth: 1024
imageHeight: 626
published: "2024-03-28T22:24:46.536Z"
updated: "2024-11-05T19:18:50.477Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>TailwindCSS is an excellent tool for streamlined styles and layouts in your web application. While it fits many use cases, I propose three scenarios that do not fit well: Pseudo-elements, focus/hover states, and transitions/animations. See how my hybrid approach, which leverages Tailwind classes + component-level scoped CSS, leads to better code readability and maintainability.</p>"
legacyId: 129
related:
  - how-to-add-leaflet-js-maps-inside-a-django-site
  - smartly-load-CSS-JS-page-load-time
  - how-to-add-social-share-buttons-to-your-website
---

## TailwindCSS is awesome!

Tailwind utility classes are a great way to build applications quickly, reduce application load time, and increase locality of behavior in your codebase. This comes from someone who has spent much time writing CSS. In fact, this blog relies on no CSS frameworks and has a <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/blob/master/static/css/main.css">main.css</a> that is over 1K lines long!

I've found that TailwindCSS is excellent for many use cases except three: <strong>pseudo-elements</strong>, <strong>focus/hover states, and transitions/animations.</strong>

When TailwindCSS was created, scoped CSS at the component level did not exist. However, with advances in front-end frameworks like React, Vue, and Svelte, you can now write CSS that is scoped with the component instead of maintaining a cascade for your entire application. I propose that scoped CSS is a superior solution to these three scenarios.

## Pseudo Elements (::before, ::after)

Let's take the following component on the <a target="_blank" rel="noopener noreferrer" href="https://johnsolly.dev/">showcase page</a> of my personal website (JohnSolly.dev).

<figure class="image"><img style="aspect-ratio:444/207;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/CleanShot%202024-03-28%20at%2018.23.47.png" alt="Text surrounded in styled quotes" width="444" height="207"></figure>

<strong>Pure Tailwind Utility Classes</strong>

Here's how it might look if we were Tailwind purists.

<pre><code class="language-html">&lt;p class="testimonial-quote max-w-[450px] break-words text-xl before:content-['\201C'] before:text-[#c3ceff] before:text-4xl before:font-serif before:relative before:top-[0.2em] before:left-[0.1em] after:content-['\201D'] after:text-[#c3ceff] after:text-4xl after:font-serif after:relative after:top-[0.3em]"&gt;
    {item.quote}
&lt;/p&gt;</code></pre>

What a mess! Now, I can hear the Tailwind fan girls dunking on me and suggesting I use @apply to reduce the # of classes. Sure, I could do that, but then I'm putting styles in another file, which brings us back to how vanilla CSS works (styles in a separate file)

<strong>Tailwind + Scoped CSS</strong>

Instead, I use a hybrid approach of Tailwind classes and scoped CSS within the .astro component to place and style the double quotes around the text. Isn't it a lot easier to scan and understand?

<pre><code class="language-html language-css">&lt;p class="testimonial-quote max-w-[450px] break-words text-xl"&gt;
     {item.quote}
&lt;/p&gt;

&lt;style&gt;
    .testimonial-quote::before,
    .testimonial-quote::after {
        display: inline-block;
        line-height: 0;
        position: relative;
        color: #c3ceff;
        font-size: 2rem;
        font-family: Georgia, serif;
    }

    .testimonial-quote::before {
        content: "“";
        top: 0.2em;
        left: 0.1em;
    }

    .testimonial-quote::after {
        content: "”";
        top: 0.3em;
    }
&lt;/style&gt;</code></pre>

## Hover/Focus States

Another place I prefer to use something other than the Tailwind is with hover + focus states. You CAN do it in Tailwind, but your class list will explode.

<figure class="image"><img style="aspect-ratio:410/230;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/CleanShot%202024-03-29%20at%2017.34.52.gif" alt="demonstration of hover animation on link cards" width="410" height="230"></figure>

<strong>Pure Tailwind Utility Classes</strong>

<pre><code class="language-html">&lt;div class="link-card text-lg rounded-lg flex opacity-80 border border-transparent transition-all duration-300 ease-in-out hover:border-purple-200 hover:opacity-100 focus-within:border-purple-200 focus-within:opacity-100"&gt;
    &lt;a
        href={href}
        target={isRelativeLink ? "_self" : "_blank"}
        class="rounded-lg py-6 px-5 no-underline text-inherit bg-accent-dark-overlay-lvl-2"
        rel={rel}
    &gt;
        &lt;h2 class="text-white text-2xl font-bold mb-4 flex justify-between group"&gt;
            &lt;span class="link-card-title group-hover:underline group-hover:text-underline-offset-2"&gt;{title}&lt;/span&gt;
            &lt;span&gt;&amp;rarr;&lt;/span&gt;
        &lt;/h2&gt;
        &lt;p&gt;{snippet}&lt;/p&gt;
    &lt;/a&gt;
&lt;/div&gt;</code></pre>

While some people are OK with reading 20 tailwind classes in a row, I find it overloaded. Sure, you could reduce the # of classes with an @apply, as mentioned earlier, but then you have to put that in another file, and you're back to how things are with vanilla CSS.

<strong>Tailwind + Scoped Vanilla CSS</strong>

In my hybrid approach, I use Tailwind for the styling, but the focus/active states are written in vanilla CSS within a scoped CSS block. When reading this code, it's clear that the border and opacity change when the element is hovered/focused.

<pre><code class="language-html">&lt;div class="link-card text-lg rounded-lg flex"&gt;
    &lt;a
        href={href}
        target={isRelativeLink ? "_self" : "_blank"}
        class="rounded-lg py-6 px-5 no-underline text-inherit bg-accent-dark-overlay-lvl-2"
        rel={rel}
    &gt;
        &lt;h2 class="text-white text-2xl font-bold mb-4 flex justify-between"&gt;
            &lt;span class="link-card-title"&gt;{title}&lt;/span&gt;
            &lt;span&gt;&amp;rarr;&lt;/span&gt;
        &lt;/h2&gt;
        &lt;p&gt;{snippet}&lt;/p&gt;
    &lt;/a&gt;
&lt;/div&gt;
&lt;style&gt;
    .link-card {
        opacity: 0.8;
        border: 1px solid transparent;
        transition:
            border-color 300ms ease-in-out,
            opacity 300ms ease-in-out;
    }

    .link-card:is(:hover, :focus-within) {
        border-color: rgb(232, 196, 249);
        opacity: 1;
    }
    .link-card:is(:hover, :focus-within) .link-card-title {
        text-decoration: underline;
        text-underline-offset: 0.2em;
    }
&lt;/style&gt;</code></pre>

With the transitions and focus/hover states moved into scoped CSS, I can clearly (and quickly!) see what is happening to the element when it is in focus or hovered. The border color changes, the opacity increases, and the link card title's underline is removed.

## Transitions/Animations

Keyframes and anything related to moving things around on the screen are a nightmare in Tailwind. Here's an example from my <a target="_blank" rel="noopener noreferrer" href="https://johnsolly.dev/">showcase page</a> for rotating a chevron symbol when the user clicks on an accordion to open my bio.

<figure class="image image-style-align-center"><img style="aspect-ratio:800/451;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/CleanShot%202024-03-29%20at%2017.36.40.gif" alt="John Solly Bio accordion opening and closing" width="800" height="451"></figure>

<strong>Pure Tailwind Utility Classes</strong>

This doesn't work precisely, but it's close to what you must do. The tricky part is that the way I have my HTML and JS written, the SVG animation happens when the parent button's \`aria-expanded\` is toggled on/off.

<pre><code class="language-html language-css">&lt;button
  class="flex items-center w-full accordion-btn"
  aria-expanded="false"
&gt;
  &lt;span class="flex-grow text-xl tracking-tight leading-none font-bold text-custom-offwhite accordion-title"&gt;
    Read More About Me
  &lt;/span&gt;
  &lt;Image
      src={accordionIcon}
      class="transition-transform duration-200 [aria-expanded='true']:[&amp;&gt;svg]:rotate-180 [aria-expanded='false']:[&amp;&gt;svg]:rotate-0" /&gt;
      // additional props
&lt;/button&gt;</code></pre>

In the following example, I use Tailwind for most styling but reserve the transform for the scoped CSS.

<strong>Tailwind + Scoped Vanilla CSS</strong>

<pre><code class="language-html language-css">&lt;button
    class="accordion-btn flex items-center w-full"
    aria-expanded="false"
&gt;
    &lt;span
        class="accordion-title flex-grow text-xl tracking-tight leading-none font-bold text-custom-offwhite"
    &gt;
        Read More About Me
    &lt;/span&gt;
    &lt;Image
        src={accordionIcon}
        ...
    /&gt;
&lt;/button&gt;

&lt;style&gt;
.accordion-btn[aria-expanded="true"] .accordion-icon {
    transform: rotate(180deg);
    transition: transform 0.2s ease;
}
.accordion-btn[aria-expanded="false"] .accordion-icon {
    transform: rotate(0deg);
    transition: transform 0.2s ease;
}
&lt;/style&gt;</code></pre>

## When I use Tailwind

TailwindCSS is my go-to for general styling and most layouts. I draw the line at pseudo-elements, hover/focus states, and transitions. I find component-level scoped CSS superior in terms of readability and maintainability in these scenarios.
