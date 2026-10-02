---
slug: free-cdn-for-17x-speed
title: Unlock 1714% Faster Site Speeds With CloudFlare's Edge Network
category: Geodev
description: Dramatically improve your website's page load speed around the world with a CDN. Find out how CloudFlare's edge network can unleash 1714% time to first byte.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/TTFB_Results.png
legacyImage: post_metaimgs/TTFB_Results.png
imageAlt: List of TTFB for cities in Asia.
imageAttribution: ""
imageWidth: 913
imageHeight: 457
published: "2022-05-23T17:13:10Z"
updated: "2024-11-05T14:03:35.327Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Dramatically improve your website's page load speed around the world with a CDN. Find out how CloudFlare's edge network can unleash 1714% time to first byte.</p>
legacyId: 49
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - cloudflare-minify-optimizations-broke-sri
  - Adding-views-likes-to-posts
---

Blogthedata.com is 1714% faster!!! Now people in Jakarta, Indonesia, can ping my site faster than a sip of coffee.

This site lives on a Linode server based in Dallas, TX because I guessed most site traffic would come from the US. Dallas is a midpoint, nearly equidistant from NYC and Los Angeles, the two most populous US cities.

Last December, I <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/Adding-views-likes-to-posts/">added likes and views to blog posts</a>. I track views by counting unique IP addresses that visit at least one post. The logic gets confused by VPNs, but it's a good approximation. It shocked me to discover 776 IPs have visited blogthedata.com, spread across <a target="_blank" rel="noopener noreferrer" href="https://ipinfo.io/tools/map/9c4e1830-8060-4ed3-ad9a-11c0780d9954">46 countries and 203 cities</a>!

![Map of over 700 unique IPs. The top three  countries are the US, Canada, and France](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220527235458-1.png)

 Now it was time to discover how blogthedata.com performs in other countries. I ran an online audit tool, <a target="_blank" rel="noopener noreferrer" href="https://speedvitals.com/ttfb-test?url=https://blogthedata.com">Speed Vitals</a>, to measure TTFB (Time to first byte) from 35 locations in the world. For cites in America, the speeds weren't too bad.

![TTFB  for US states. Values are between 390ms and 1500ms with most under 1000ms](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220527235646-2.png)

But for cities far from Dallas, it was slowwww. Most took over a second, some over 2 seconds!!!

<img class="image_resized" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220527235912-4.png" alt="TTFB for countires in Asia. Values range from 1,400ms to 2,300ms" width="537" height="332">

To speed things up, I used CloudFlare's <a target="_blank" rel="noopener noreferrer" href="https://www.cloudflare.com/network/">edge network</a> to cache pages on different servers around the world. Instead of only being in Dallas, Blogthedata.com could be EVERYWHERE. Best of all, CloudFlare's edge network is free with up to three page rules.

## <i>CloudFlare's Edge network</i>

![Cloudfare Map of Edge Networks](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/cloudfare_map.svg)

There is a big drawback to using an edge network. CloudFlare does not guarantee each node will have the latest snapshot of your site. The smallest value possible is <strong>&nbsp;two hours</strong>. This means site changes can take up to two hours to propagate. For websites requiring up-to-date content, this is a deal breaker. Still, with <a target="_blank" rel="noopener noreferrer" href="https://support.cloudflare.com/hc/en-us/articles/218411427-Understanding-and-configuring-Cloudflare-Page-Rules-Page-Rules-Tutorial-">page rules</a> you can be smart and only cache the static portions of your site and leave out dynamic content.

For static sites, it's a non-issue. If it takes two hours to see new posts, I guess you'll just have to wait!

The way the caching works is that CloudFlare caches pages on the edge based on page rules

![CloudFlare page rules page showing a single rule of \*/blogthedata.com/\*](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/cloudflare_page_rule.png)

I cached every page on blogthedata.com using a wildcard matching all subpages. After applying the rule, I eagerly waited two hours for a TTFB re-test. I was delighted to see <a target="_blank" rel="noopener noreferrer" href="https://speedvitals.com/ttfb-test?url=https://blogthedata.com">massive speed increases across the board</a>. 5-10x increases in the US. 

![TTFB for US states after making changes. Values range from 90ms to 300ms](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/us_speeds_post_cdn.png)

The gains are even more apparent in Asia with 10-15x increases. In Jakarta, Indonesia, users went from a 1,200ms TTFB to 70ms.

![TTFB for counrtries in Asia after making changes. Values range from 31ms to 300ms](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/asia_speeds_post_cdn.png)

You can see CloudFlare's edge network in play by checking HTTP response headers. If you see 'cf-cache-status HIT', that means CloudFlare served the resource instead of your hosting server.

![Image of HTTP headers in chrome dev tools. cf-cache-status is highlighted as HIT.](https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/chrome_dev_tools_cloudflare.png)

## Conclusion

Adding your website to a CDN edge network can improve page load dramatically for users accessing your site around the world. After adding my site to CloudFlare, some locations had a 17x faster TTFB (time to first byte). The drawback is that it can take up to two hours to see new content.

Add some (or all) of your site to a CDN edge network and reap the benefits of a faster TTFB for your users!
