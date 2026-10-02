---
slug: how-to-get-perfect-linting-compliance
title: "Adhering to PEP 8 Style Guidelines: Cleaning Up Blogthedata.com Code"
category: dev-tools
description: Rid your code of errors, bugs, stylistic errors, and suspicious constructs. Use linters to take your app to the next level!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/python_logo_Ca9SNv5.png
legacyImage: post_metaimgs/python_logo_Ca9SNv5.png
imageAlt: Python logo
imageAttribution: ""
imageWidth: 1280
imageHeight: 800
published: "2022-05-06T17:35:08Z"
updated: "2026-09-07T14:25:05.469Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Rid your code of errors, bugs, stylistic errors, and suspicious constructs. Use linters to take your app to the next level!</p>
legacyId: 39
related:
  - implement-continuous-integration-github-actions
  - how-to-get-a-perfect-mozilla-observatory-score
  - finding-reliable-information
---

Blogthedata.com is coming together! We now have <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/google-lighthouse-perfect-score/">perfect* Google Lighthouse score</a>, open issues\[1, 2\] to achieve a <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-a-perfect-mozilla-observatory-score/">perfect* Mozilla Observatory</a> score, and <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-100-percent-unit-test-coverage/">100% unit test coverage</a>.

Now, what about the code style? That's where linting comes in. There are <a target="_blank" rel="noopener noreferrer" href="https://www.slant.co/topics/2692/~best-python-code-linters">several linters</a> for Python, I use Pylint.

VScode has <a target="_blank" rel="noopener noreferrer" href="http://code.visualstudio.com/docs/python/linting">native Pylint integration</a>. Pylint analyzes your code for several issues including very Pythonic things like ensuring <a target="_blank" rel="noopener noreferrer" href="https://peps.python.org/pep-0008/#naming-conventions">variables conform to snake casing</a> (sorry JavaScript 😆) as well as data structure suggestions such as when it might be better to <a target="_blank" rel="noopener noreferrer" href="https://pylint.pycqa.org/en/latest/messages/refactor/consider-using-tuple.html">use a tuple over a list</a>. Most Pylint suggestions are based on Python's famous <a target="_blank" rel="noopener noreferrer" href="https://peps.python.org/pep-0008/">PEP 8 style guide</a> authored by the great Guido van Rossum.

Now, it's time to spill the beans. I don't 'exactly' have 100% Pylint compliance. I added the following to my VScode settings.json to ignore some Pylint checkers:

<pre><code class="language-python"># settings.json
{
    "python.linting.pylintArgs": [
        "--disable=C0301",
        "--disable=C0114",
        "--disable=C0115",
        "--disable=C0116",
        "--disable=E0401",
    ]
}</code></pre>

<a target="_blank" rel="noopener noreferrer" href="https://pylint.pycqa.org/en/latest/messages/convention/line-too-long.html">C0301</a> - Line too Long

I don't like lines being too long, but sometimes code just makes more sense on one line even if it’s long. I do include the following rulers in VScode to see PEP 8's line length guidelines within the editor.

<pre><code class="language-python"># settings.json
{"editor.rulers": [79, 120]}</code></pre>

## Rulers in VScode

<img class="image_resized" style="width:800px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image-20220506115820-2.png" alt="Screenshot of vscode with vertical bars showing rulers at 79 and 120 characters">

<a target="_blank" rel="noopener noreferrer" href="https://pylint.pycqa.org/en/latest/messages/convention/missing-module-docstring.html">C0114</a>, <a target="_blank" rel="noopener noreferrer" href="https://pylint.pycqa.org/en/latest/messages/convention/missing-class-docstring.html?highlight=C0115">C0115</a>, <a target="_blank" rel="noopener noreferrer" href="https://pylint.pycqa.org/en/latest/messages/convention/missing-function-docstring.html?highlight=C0116">C0116</a>, (missing class, module, function docstrings)

I am no stranger to documentation. I love documenting things! That being said, I will soon be 'reactifying' blogthedata.com which will drastically change code architecture. Once I split the front and backend of the app, I'll turn these checkers back on so I can crank out documentation.

<a target="_blank" rel="noopener noreferrer" href="https://pylint.pycqa.org/en/latest/messages/error/import-error.html?highlight=E0401">E0401</a> - import-error

I haven't quite figured this one out. The error is supposed to be about a failed import, but I’ve run into cases where Pylint says the import is failing, but it's clearing working in my code. I turned the error off until I can figure out why Pylint is confused.

Other than those exclusions, blogthedata.com is Pylint compliant and attempts to follow PEP 8 style guidelines wherever possible.

Get a linter and clean up yo code!
