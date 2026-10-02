---
slug: TypeScript-revealed-210-issues-JavaScript-codebase
title: Adding TypeScript to a JavaScript Project | A Step-by-Step Guide
category: dev-tools
description: Add TypeScript to your JavaScript project by converting .js files to .ts and fixing any compilation errors. Follow this guide for detailed instructions.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/TypeScript.webp
legacyImage: post_metaimgs/TypeScript.webp
imageAlt: Meta Image
imageAttribution: ""
imageWidth: 1009
imageHeight: 286
published: "2022-07-19T21:59:53.847Z"
updated: "2022-07-19T21:59:53.847Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Add TypeScript to your JavaScript project by converting .js files to .ts and fixing any compilation errors. Follow this guide for detailed instructions.</p>
legacyId: 78
related:
  - I-resolved-150-linting-issues-with-eslint
  - I-replaced-for-loops-with-for-of-loops-cleaner
  - how-to-implement-subresource-integrity-django
---

All I needed to do to add TypeScript to my JavaScript project was install TypeScript, add a config file, and change the file extensions from .js to .ts. You can see the code change in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoAsteroids/pull/22/files">this PR</a>.

<pre><code class="language-bash">sudo npm install -g typescript</code></pre>

<pre><code class="language-bash">// tsconfig.json
{
    "compilerOptions": {
        "target": "ES6",
        "outDir": "./built",
        "rootDir": "./src",
        "strict": true
    }
}</code></pre>

Now, when I run <code>$ tsc</code> TypeScript files are compiled into JavaScript and placed in a folder named ./built. Although the app works, it's not flexing TypeScript until I add types to my variables and functions and resolve the 210 warnings spit out to the console on the compile step.

<pre><code class="language-bash">Found 210 errors in 9 files.

Errors  Files
    39  src/asteroids.ts:18
    27  src/canvas.ts:5
    29  src/collisions.ts:34
     2  src/keybindings.ts:10
    42  src/lasers.ts:22
     9  src/scoreLevelLives.ts:39
    28  src/ship.ts:134
    30  src/soundsMusic.ts:8
     4  src/utils.ts:9</code></pre>

Stay tuned for a future post about my journey to resolving all these errors!
