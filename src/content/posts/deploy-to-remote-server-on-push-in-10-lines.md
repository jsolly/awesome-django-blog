---
slug: deploy-to-remote-server-on-push-in-10-lines
title: "Simplifying Automatic Deployments: Using Git Pull With CI Workflow"
category: dev-tools
description: "Simplifying Automatic Deployments: How I used an SSH job in my CI workflow to deploy updates to blogthedata.com"
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/deploy_linode_gitactions.webp
legacyImage: post_metaimgs/deploy_linode_gitactions.webp
imageAlt: Screenshot of Linode deployment code included in post
imageAttribution: ""
imageWidth: 297
imageHeight: 203
published: "2022-07-24T22:28:40.818Z"
updated: "2024-11-06T13:40:06.966Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>Simplifying Automatic Deployments: How I used an SSH job in my CI workflow to deploy updates to blogthedata.com</p>"
legacyId: 89
related:
  - how-to-get-a-perfect-mozilla-observatory-score
  - implement-continuous-integration-github-actions
  - code-analysis-and-pip-dependency-check-in-GitHub
---

I was researching ways to automatic deployments for blogthedata.com when I push code into main and everything I came across was super complicated. The solution I came up with was to just add a job to my existing CI workflow to SSH into my server and do a <code>git pull</code>. I implemented it in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/124">this PR</a>.

<pre><code class="language-yaml">  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Linode
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd blogthedata
          git pull</code></pre>

Check out the <a target="_blank" rel="noopener noreferrer" href="https://github.com/appleboy/scp-action">AppleBoy Repo</a> for the latest instructions.

## Caveats 

1 - If I need to perform a database migration, I still have to do that manually.
