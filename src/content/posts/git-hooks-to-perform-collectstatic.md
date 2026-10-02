---
slug: git-hooks-to-perform-collectstatic
title: Using Pre-commit Hooks to Automate Collectstatic in Django
category: dev-tools
description: Use pre-commit hooks to automate collectstatic in Django to keep production and QA environments in sync. Save time and make the overall process more efficient.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/githooks.png
legacyImage: post_metaimgs/githooks.png
imageAlt: A hook going through the word 'git'
imageAttribution: ""
imageWidth: 2000
imageHeight: 948
published: "2022-01-24T16:31:25Z"
updated: "2022-01-24T16:31:25Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Use pre-commit hooks to automate collectstatic in Django to keep production and QA environments in sync. Save time and make the overall process more efficient.</p>
legacyId: 13
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - conventional-commits
  - automate-python-testing-linting-pre-commit-hooks
---

After modifying static files (ckeditor, fonts, etc), I needed to run:

<code>Python3 manage.py collectstatic</code>

in both environments to sync QA and prod environments. A web search for 'commit static files to source control' reveals this <a target="_blank" rel="noopener noreferrer" href="https://stackoverflow.com/questions/41558258/should-i-add-django-admin-static-files-to-my-git-repo/41558803">StackOverflow Question</a>. The top answerer had an interesting approach:

<blockquote><p>While you can absolutely check these files in, I typically recommend not checking in the collected static files into git (we use .gitignore to ignore them). Instead, we call&nbsp;<code>collectstatic</code>&nbsp;during our build/deploy steps so that if anyone ever adds new static files, they are collected and copied to the proper output directory for serving by nginx or sent up to s3. If you want to check them into git, I would recommend having collectstatic as a precommit hook so that no one accidentally forgets to run it when adding a new static file.</p></blockquote>

I've never used precommit hooks, but the <a target="_blank" rel="noopener noreferrer" href="https://git-scm.com/docs/githooks">git hooks doc</a> is super straight-forward. If you're using VSCODE, you'll first need to remove the file exclusion of .git so that the IDE can see the .git folder in the catalog view.

Settings -\> Files:exclude

Then, you copy the pre-commit.sample file inside .git/hooks and rename it to pre-commit. Inside pre-commit, I add one line:

<code>~/blogthedata/venv/bin/python3 ~/blogthedata/django_project/manage.py collectstatic --noinput</code>

Now, whenever youdo  a git commit, the collectstatic command runs to ensure static files collect.

A final step is to remove 'static/' from .gitignore so git recognizes and uploads all the static files.

Now I you don't have to run collectstatic on prod!
