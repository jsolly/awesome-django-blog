---
slug: I-resolved-150-linting-issues-with-eslint
title: Using ESlint and Husky to Improve Code Quality in a Game Project
category: dev-tools
description: ESlint helps you find errors in your JavaScript code. It's also can format code to make it easier to read. Everyone should use a linter!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/eslint.webp
legacyImage: post_metaimgs/eslint.webp
imageAlt: Eslint logo
imageAttribution: ""
imageWidth: 512
imageHeight: 512
published: "2022-07-19T21:26:56.510Z"
updated: "2026-09-07T14:25:05.488Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>ESlint helps you find errors in your JavaScript code. It's also can format code to make it easier to read. Everyone should use a linter!</p>
legacyId: 76
related:
  - implement-continuous-integration-github-actions
  - TypeScript-revealed-210-issues-JavaScript-codebase
  - code-analysis-and-pip-dependency-check-in-GitHub
---

This week I used ESlint to resolve over 150 issues in a game I created, <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoRoids">GeoAsteroids</a>. You can see the work in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoAsteroids/pull/20/files">this PR</a>. I also use a pre-commit hook to lint and format code pushing to remote. All I had to do was install a tool called Husky, and add a pre-commit file in the .github folder. pre-commit runs:

<pre><code class="language-bash">npm run lint-fix</code></pre>

which is defined in my package.json file,

<pre><code class="language-json">// package.json
"scripts": {
  ...
  "lint": "eslint . --ext .js,.ts",
  "lint-fix": "eslint . --fix --ext .js,.ts",
},</code></pre>

<code>lint-fix</code> is run in the pre-commit hook and <code>lint</code> is run during the CI build process with Git Actions. This way, I fix the issues locally before the code is committed, and it's rechecked before it makes it into a remote branch.

Add a linter to your codebase today!
