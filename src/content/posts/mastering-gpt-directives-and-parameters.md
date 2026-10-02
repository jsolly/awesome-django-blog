---
slug: mastering-gpt-directives-and-parameters
title: "Mastering GPT: A Guide to Directives and Parameters"
category: productivity
description: Customize GPT with directives and parameters. Improve your GPT skills and get the most out of this powerful tool.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/referenceDirective.webp
legacyImage: post_metaimgs/referenceDirective.webp
imageAlt: John Solly Headshot
imageAttribution: ""
imageWidth: 455
imageHeight: 316
published: "2022-12-27T16:13:02.388Z"
updated: "2022-12-27T16:13:02.388Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn about the different directives and parameters used to customize GPT for your specific needs. This blog post will explain how to use directives such as analyze, cross-reference, write, and disable and parameters like Context and Pretext. Improve your GPT skills and get the most out of this powerful tool.</p>
legacyId: 109
related:
  - optimizing-gpt-for-nlp-tips-and-tricks
  - exploring-new-ideas-with-gpt
---

## Intro

I have discovered and tested certain directives and parameters for GPT through trial and error, along with others in the <a target="_blank" rel="noopener noreferrer" href="https://discord.com/invite/openai">OpenAI Discord community</a>. This information is not officially documented by OpenAI, but I hope it is helpful as a pseudo-documentation. Please note that this information is not endorsed by OpenAI, but rather is syntax that appears to be effective. <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/optimizing-gpt-for-nlp-tips-and-tricks/">Check out More GPT Tips and Tricks</a>.

## Directives

Directives are action verbs that allow you to instruct GPT to do different things. <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/optimizing-gpt-for-nlp-tips-and-tricks/#directives">Learn more about bracket directive syntax</a>. 

A directive is a term used to tell GPT you are instructing it to do something. Directives, are written in a specific format and can include action verbs such as "write," "do," or "type." Directives may also include additional conditions that must be followed, indicated by a colon (:). GPT processes directives in the order they are written and can follow logical operations such as AND, OR, and XAND (which represents "not AND"). The general format looks like this:

<blockquote><p>[directiveName: directObject1...directObjectN]</p></blockquote>

### analyze:

Examine the structure of a text.

<blockquote><p><strong>prompt:</strong>[analyze: "The quick brown fox jumped over the lazy dog"][write:verbs]</p><p><strong>reply:</strong> jump</p></blockquote>

### cross-reference:

Compare input text to something else

<blockquote><p><strong>prompt: </strong>[metaphorical analysis:"I dreamt I was being chased by a lion and a lamb saved me"][cross-reference: The Holy Bible]</p><p><strong>reply: </strong>In the context of this dream, the lion represents danger or threat while the lamb represents innocence or purity. The metaphor could potentially be referencing the biblical passage in Isaiah 11:6, which states "The wolf will live with the lamb, the leopard will lie down with the goat, the calf and the lion and the yearling together; and a little child will lead them." This passage speaks of a time of peace and harmony, where even the most ferocious of animals will lay down their aggression. In the dream, the lamb symbolizes this peaceful resolution, rescuing the dreamer from the danger represented by the lion. This could be interpreted as a metaphor for the power of innocence and goodness to overcome even the most formidable challenges.</p></blockquote>

### disable: 

Turn off a GPT feature. See \[Parameters\] to see what can be disabled.

<blockquote><p>prompt: [disable: "Pretext" AND "Context"]</p></blockquote>

## write:

Tells GPT to 'write' something. 

<blockquote><p><strong>prompt:</strong> [write: a noun]</p><p><strong>reply:</strong> Apple</p></blockquote>

## Parameters

<strong>Context -</strong> GPT may include additional information or "fluff" in its replies. In most cases, the responses can still be understood with Context disabled.

<strong>Pretext:</strong> The introductory statement often appearing at the beginning of a reply, such as "Sure, I can answer your question about X."\*

<span class="text-tiny">*it is important to note that the Pretext is also where GPT will warn you if it does not have enough information or is unsure about something, so you may want to leave it enabled for this reason.</span>
