---
slug: I-made-my-code-async-its-388-percent-faster
title: Speed Up REST Calls With AsyncIO | Get 388% Faster Results
category: web-dev
description: Use asyncio to speed up your REST calls and get 388% faster results. Learn how to make multiple requests without waiting for each response.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/async_code.png
legacyImage: post_metaimgs/async_code.png
imageAlt: Screenshot of asynchronous Python code
imageAttribution: ""
imageWidth: 1396
imageHeight: 832
published: "2022-06-02T20:45:55Z"
updated: "2022-06-02T20:45:55Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Use asyncio to speed up your REST calls and get 388% faster results. Learn how to make multiple requests without waiting for each response.</p>
legacyId: 59
related:
  - migrating-to-django-4x
  - how-to-implement-content-security-policy-django
  - implement-infinite-scroll-in-django-with-htmx
---

The blog roadmap page makes several synchronous REST calls to the GitHub API to fetch issues. I thought I could speed things up by making them asynchronous. I can make several REST calls with async without waiting for each response.

## Synchronous

<pre><code class="language-python">import requests
def make_request(url):
    return requests.request(method="GET, url=url)
URLS = [url1, url2, url3]
response1, response2, response3 = map(url, make_request)</code></pre>

## Asynchronous

<pre><code class="language-python">import aiohttp
import asyncio
async def make_request(session, url):
    async with session.get(url) as resp:
        return await resp.json()

async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(make_request(session, url)))
        return await asyncio.gather(*tasks)

urls = [url1, url2, url3]
response1, response2, response3 = asyncio.run(main(urls))</code></pre>

I ran both versions five times with these results:

<code>synchonous_time (in seconds) = [1.2, 1.3, 1.5, 1.3]</code>

<p style="margin-left:40px;"><code>synchonous_average = 1.32 seconds</code></p>

<p style="margin-left:40px;">&nbsp;</p>

<code>asynconous_time (in seconds) = [0.3, 0.4, 0.3, 0.4, 0.3]</code>

<p style="margin-left:40px;"><code>asynconous_average = 0.34 seconds</code></p>

That's 1.32/0.34 \* 100 = <strong>388% faster</strong>!

You won't notice because site pages are cached on <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/free-cdn-for-17x-speed/">Cloudflare's edge network</a>, but it was fun to find a good use case for async and see the benefits for myself! The magic happens on <strong>lines 10 - 12,</strong> where requests are added to a task list. The code waits on <strong>line 12</strong>, but it's collecting responses as they come back instead of one at a time.

## Conclusion

Async is useful for I/O bound tasks. Instead of making requests one at a time, I used <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/asyncio/">asyncio</a> to make them asynchronous. The result was a 388% speed increase in getting back responses from the GitHub API.
