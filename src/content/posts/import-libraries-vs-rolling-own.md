---
slug: import-libraries-vs-rolling-own
title: Importing Libraries vs ‘Rolling Your Own’
category: productivity
description: Sometimes you should import functionality. Other times, write the code yourself. At Esri, we benefitted from leveraging another team's code.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/idea_coming_out_of_box_l7p9JwK.png
legacyImage: post_metaimgs/idea_coming_out_of_box_l7p9JwK.png
imageAlt: A hand coming out of a box with a lightbulb
imageAttribution: ""
imageWidth: 1546
imageHeight: 1920
published: "2021-12-28T07:34:45Z"
updated: "2021-12-28T07:34:45Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p style="text-align:start;">Sometimes you should import functionality. Other times, write the code yourself. At Esri, we benefitted from leveraging another team's code.</p><p style="text-align:start;">&nbsp;</p>
legacyId: 3
related:
  - how-many-manual-qa-do-you-need
  - inspiring-aphorisms-axioms
  - mastering-intuition-pumps-essential-terms-guide
---

Once upon a time at Esri, our codebase conflicted with code written by the JSAPI team - on which we built ArcGIS Dashboards.

In the early days of the JSAPI, it didn't have all the functionality and customization we wanted, so we coded a lot of what we needed ourselves. Unfortunately, as the JSAPI team began working on features we had already implemented ourselves, it broke Dashboards.

Seeing that the API team had made a lot of progress and improved considerably, we began adjusting our codebase to leverage their code to offload our 'boutique' development.

The benefits were enormous. I remember combing through the backlog and closing dozens of bugs that no longer existed because we were importing the API's libraries instead of using our own code. Another added benefit was that we no longer needed to spend as much QA time on these functional areas because our team did not write most of the code!

Moral of the story - Sometimes it makes sense to import functionality instead of ‘rolling your own.’ The benefits can include less bugs, reduced QA requirements, and less stress!
