---
slug: conventional-commits
title: "Git Good: Making the Move to Conventional Commits"
category: dev-tools
description: Learn the importance of good commit messages and the structure of Conventional Commits with an example in VScode.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/conventionalCommits.png
legacyImage: post_metaimgs/conventionalCommits.png
imageAlt: The text 'Conventional Commits' with a blue background.
imageAttribution: ""
imageWidth: 3850
imageHeight: 2170
published: "2022-01-23T19:18:48Z"
updated: "2022-01-23T19:18:48Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn the importance of good commit messages and the structure of Conventional Commits with an example in VScode.</p>
legacyId: 12
related:
  - Adding-views-likes-to-posts
  - two-weird-reasons-I-love-unit-tests
  - mastering-intuition-pumps-essential-terms-guide
---

Recently read <a target="_blank" rel="noopener noreferrer" href="https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/">this article</a> by Natalie Pina who stresses the importance of writing good commit messages. I'm guilty. Many commits are simply, "WIP" which is short for "Work in Progress." That changes today! I now use a format called 'Conventional Commits'

Conventional commits follow a structure

<pre><code class="language-python">&lt;type&gt;[optional scope]: &lt;description&gt;

[optional body]

[optional footer(s)]</code></pre>

The \<type\> is one of the following options:

<ul><li><code>feat</code>&nbsp;– a new feature is introduced with the changes</li><li><code>fix</code>&nbsp;– a bug fix has occurred</li><li><code>chore</code>&nbsp;– changes that do not relate to a fix or feature and don't modify src or test files (for example updating dependencies)</li><li><code>refactor</code>&nbsp;– refactored code that neither fixes a bug nor adds a feature</li><li><code>docs</code>&nbsp;– updates to documentation such as a the README or other markdown files</li><li><code>style</code>&nbsp;– changes that do not affect the meaning of the code, likely related to code formatting such as white-space, missing semi-colons, and so on.</li><li><code>test</code>&nbsp;– including new or correcting previous tests</li><li><code>perf</code>&nbsp;– performance improvements</li><li><code>ci</code>&nbsp;– continuous integration related</li><li><code>build</code>&nbsp;– changes that affect the build system or external dependencies</li><li><code>revert</code>&nbsp;– reverts a previous commit</li></ul>

The \<scope\> states how large the change is and what it touches in the existing codebase. The \<description\> describes what is changed and the \[body\] goes into more context/background (if needed). Finally, the footer is used to reference any related dev tasks living in tools such as Jira or BugZilla.

I'm not using a formal bug tracking tool, but I could add unique ids to each bug/enhancement to reference in the footer of the commit.

Here's an example in action!

<pre><code class="language-python">fix: fix foo to enable bar

This fixes the broken behavior of the component by doing xyz. 

BREAKING CHANGE
Before this fix foo wasn't enabled at all, behavior changes from &lt;old&gt; to &lt;new&gt;

Closes D2IQ-12345</code></pre>

## Implementing in VScode

There is a plugin called <a target="_blank" rel="noopener noreferrer" href="https://marketplace.visualstudio.com/items?itemName=vivaxy.vscode-conventional-commits&amp;ssr=false#overview">Conventional Commits</a> that makes this super straight forward. Once you install the plugin, you'll get a little circle in VScode:

<img class="image_resized" style="height:244px;width:469px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/conventional_commits_in_cscode_ui.png" alt="Conventional Commits icon in VScode">

You can see in the image above I've already staged a change...a modification to my .gitignore file.

<img class="image_resized" style="height:229px;width:431px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/staged_commit_in_vscode.png" alt="Staged commit in Vscode">

You start the commit process by clicking that new circle. The rest of the steps are guided and self-explanatory. Once you finish, push away!

## This is what the commits look like in Git

## <img class="image_resized" style="height:230px;width:801px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/commit_view_github.png" alt="A list of commits in GitHub">

## If you click on one of the commits, you see the whole thing

<img class="image_resized" style="height:171px;width:800px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/single_commit_view.png" alt="A view of a single commit in GitHub">I am quite happy with conventional commits. I can hear my future self thanking me. Hope you like them too! If you use another style of commits, let me know in the comments!
