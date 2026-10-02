---
slug: how-many-manual-qa-do-you-need
title: "Find the Optimal QA to Developer Ratio: Data-Driven Hiring Decisions"
category: productivity
description: Learn how to estimate the ideal QA to Developer ratio for software development teams by considering variables and using data-driven approaches.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/tensorFlowModel.png
legacyImage: post_metaimgs/tensorFlowModel.png
imageAlt: Headshot of John Solly
imageAttribution: ""
imageWidth: 983
imageHeight: 1000
published: "2022-03-14T15:27:26Z"
updated: "2026-09-07T14:25:05.458Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to estimate the ideal QA to Developer ratio for software development teams by considering variables and using data-driven approaches.</p>
legacyId: 22
related:
  - implement-continuous-integration-github-actions
  - Adding-views-likes-to-posts
  - compress-minify-assets-69-percent-faster-page-load
---

Recently came across a Stack Overflow thread discussing the ideal QA to Developer ratio for software development teams. According to the commenters, dev teams can range from no manual testing at all to a 1:1 ratio of dev to QA. My first thought was:

<blockquote><p>"Can we find a way to estimate how many QA engineers are needed based on a set of criteria that can be measured in any software project?"</p></blockquote>

After scanning the thread and reviewing a few other resources, I noticed patterns in how people justified more/less QA. Here are the variables I extracted:

<strong>Number of Developers</strong> - Self-explanatory

<i><strong>Number of lines of code</strong></i> - A naïve way to estimate code complexity and application size

<strong>Danger of Failure</strong> - How nasty would a bug be if introduced? A frustrating day at the office or lives lost?

<strong>Team Maturity&nbsp;</strong> \- How experienced are the team with each other and development? A group of new grads or a seasoned development team working together for many years?

<strong>Degree of Change in Codebase&nbsp;</strong> \- How volatile is the development effort? Is the product in beta and still has many moving pieces, or is it a mature product with predictable development?

<strong>Leverage existing libraries</strong> - If you're building an application that relies on 3rd party code, you won't need to invest as much time testing because the codebases you are leveraging have hopefully already been tested.

<strong>Amount of unit testing</strong> - How much unit test coverage is there? None, 100%?

I experimented with these parameters in Google Sheets using RANDBETWEEN( ) to input numbers like <i>Lines of Code</i> or <i>Number of Developers. Then I used</i> my judgment to estimate the number of QA engineers needed for a project.

<img class="image_resized" style="height:73px;width:400px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/csv_output.png" alt="CSV output of manual classification of QA engineers needed">

With ~200 rows manually classified, I brought this up with my friend Aviv, who thought we could fit a model to the dataset to predict the number of QA Engineers needed for any situation. After importing the data into a <a target="_blank" rel="noopener noreferrer" href="https://colab.research.google.com/drive/1rBKdTwgBrF02dXLpyImKsiK_hMjSOYow?usp=sharing">Jupyter notebook</a>, he trained a model using TensorFlow and exported the results to CSV,

Here's a pair plot of the model's output. You can see the full report included in the notebook linked above.

<img class="image_resized" style="height:407px;width:400px;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/tensorflow_model_output.png" alt="Tensorflow Model Output">

The model correctly discovered that when I manually labeled <i><strong>Number of QA Engineers</strong></i> needed, I mainly leveraged <i><strong>Number of Developers</strong></i><strong>,&nbsp;</strong> <i><strong>Danger of Failure</strong></i>, and <i><strong>Degree of change in Codebase</strong></i>.

## Conclusions

This was an initial attempt to explore whether QA Engineer hiring decisions could be data-driven. I wouldn't put too much weight into the final model, but it was a fun learning exercise! If I wanted to take this work further, I would dive deeper into the variables and devise a way to weigh each appropriately. I would also incorporate the whole QA testing strategy, including hiring SDETS (Software Developers in Test), offshore QA resources, and other 3rd party testing teams.

What do you think? Let me know in the comments 😁
