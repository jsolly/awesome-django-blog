---
slug: two-weird-reasons-I-love-unit-tests
title: "Unit Tests as a Design Tool: Increase Coverage and Improve Your Code"
category: dev-tools
description: Discover how unit tests can be a design tool to improve your code and increase coverage. Learn how to fix multiple bugs without re-running your code.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/testingPyramid.png
legacyImage: post_metaimgs/testingPyramid.png
imageAlt: Unit, Acceptance, UI test pyramid.
imageAttribution: ""
imageWidth: 500
imageHeight: 335
published: "2022-05-13T03:11:06Z"
updated: "2022-05-13T03:11:06Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Discover how unit tests can be a design tool to improve your code and increase coverage. Learn how to fix multiple bugs without re-running your code.</p>
legacyId: 44
related:
  - implement-continuous-integration-github-actions
  - test-strategy-no-existing-tests
  - integration-tests-are-a-scam-i-wrote-them-anyway
---

The benefits of using unit tests in your code cannot be overstated. Not only do they serve as a powerful refactoring tool, but they also act as a design tool to improve the quality of your code. If your application currently lacks unit tests, now is the time to start the journey toward <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-100-percent-unit-test-coverage/">100% unit test coverage</a>.

## Unit tests as a refactoring tool

Without unit tests, refactoring can be a tedious process. It typically involves attempting to run or compile your code, reading a single stack trace, and fixing a single bug. With unit tests, however, this process becomes much more efficient. When multiple unit tests fail, you can fix multiple bugs simultaneously, saving you significant time.

## Unit tests as a design tool

To convince you further<strong>, </strong> learn about why <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/integration-tests-are-a-scam-i-wrote-them-anyway/">integration tests are a scam</a> and why you should write unit tests instead. Another favorite reason I love unit tests is that they are a fabulous design tool.

<blockquote><p>It's difficult to write simple tests for complicated code.</p><p>- John Solly</p></blockquote>

In addition to their usefulness as a refactoring tool, unit tests also serve as an excellent design tool. Writing simple tests for complicated code can be difficult, so the implementation probably has room for improvement. I <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/test-strategy-no-existing-tests/">followed the TDD approach for my blog "blogthedata.com"</a> and found missing coverage across several files. 

<pre><code class="language-python">Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
blog/templates/blog/categories.html        42      2    95%   35-36
blog/templates/blog/home.html              47     19    60%   33-52
blog/templates/blog/search_posts.html      50     19    62%   36-55
blog/templates/blog/user_posts.html        37     19    49%   20-39
---------------------------------------------------------------------
TOTAL                                    1164     59    95%</code></pre>

I discovered that I had duplicated the same pagination code across multiple files in my application. Rather than writing separate tests for the same logic in various locations, I chose to refactor the code by moving it into a separate file and utilizing <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/templates/builtins/">Django's {% include %} tag</a> to inherit it into the four templates.  
  
By taking this approach, I achieved 100% code coverage after re-running my tests, without having to write a single additional test. This is a great example of how unit tests can be used as a design tool to improve the quality of your code and make it more maintainable.
