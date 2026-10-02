---
slug: optimizing-gpt-for-nlp-tips-and-tricks
title: "Optimizing GPT for Natural Language Processing: Tips and Tricks"
category: productivity
description: Optimize GPT for NLP with these tips and tricks. Unlock its full potential for text generation, code completion and more!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/ChatGPT_2hFjyq8.webp
legacyImage: post_metaimgs/ChatGPT_2hFjyq8.webp
imageAlt: ChatGPT Logo
imageAttribution: https://img.fresherslive.com/latestnews/images/articles/origin/2022/12/13/how-to-bypass-chat-gpt-filter-63981171eb5d8-1670910321.jpg
imageWidth: 646
imageHeight: 605
published: "2022-12-22T16:48:32.971Z"
updated: "2024-05-04T23:49:50.897Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>GPT is a powerful natural language processing tool that can be optimized for various tasks, such as text generation, code completion, and text summarization. This blog post will look at tips and tricks to get the most out of GPT.</p>
legacyId: 107
related:
  - Adding-views-likes-to-posts
  - exploring-new-ideas-with-gpt
  - mastering-gpt-directives-and-parameters
---

<h2 id="Intro">Introduction</h2>

GPT (Generative Pre-training Transformer) is a popular language model developed by OpenAI that has revolutionized the field of natural language processing (NLP). It can generate human-like text and has been used in various applications such as language translation, summarization, and even generating code.

In this blog post, we will go over some tips and tricks for working with GPT. These tips will be handy for those who have some basic familiarity with GPT and want to take their skills to the next level. <span style="background-color:rgb(255,255,255);color:rgb(0,0,0);"><span style="-webkit-text-stroke-width:0px;display:inline !important;float:none;font-family:system-ui, Helvetica, Arial, sans-serif;font-size:20px;font-style:normal;font-variant-caps:normal;font-variant-ligatures:normal;font-weight:400;letter-spacing:normal;orphans:2;text-align:start;text-decoration-color:initial;text-decoration-style:initial;text-decoration-thickness:initial;text-indent:0px;text-transform:none;white-space:normal;widows:2;word-spacing:0px;">Please note that this information is not endorsed by OpenAI, but rather is syntax that appears to be effective.</span></span>

<h2 id="learning-resources">Learning Resources</h2>

First, here's a list of resources I've used to improve my prompt engineering skills.

<a target="_blank" rel="noopener noreferrer" href="https://github.com/f/awesome-chatgpt-prompts">Awesome ChatGPT Prompts (GitHub repo)</a>

<a target="_blank" rel="noopener noreferrer" href="https://github.com/dair-ai/Prompt-Engineering-Guide">Prompt Engineering Guide (GitHub repo)</a>

<a target="_blank" rel="noopener noreferrer" href="https://github.com/openai/openai-cookbook">OpenAI Cookbook (GitHub Repo)</a>

<a target="_blank" rel="noopener noreferrer" href="https://github.com/sw-yx/ai-notes">AI Notes (GitHub Repo)</a>

<a target="_blank" rel="noopener noreferrer" href="https://learnprompting.org/docs/intro">LearnPrompting.org</a>

<a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/mastering-gpt-directives-and-parameters/">GPT Directive and Parameter Guide (blogthedata.com)</a>

## Useful Words and Phrases

<strong>Write a concise answer</strong> - Ensures GPT's reply is as short and to the point as possible.

<strong>Do not provide explanations</strong> - GPT will often offer explanations in its reply. If you want a more natural conversation like an <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-use-ChatGPT-for-GeoDev-Interview-practice/">AI job interview</a>, Including this phrase will ensure you only get dialog back.

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_Iu6jxbT.png" alt="GPT output of the above prompt"></figure>

To get a look 'under the hood,' simply append, 'Explain how you arrived at your answer, step-by-step.'

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_Jv0GYBE.png" alt="GPT output of the above prompt"></figure>

Much more informative!

<strong>Optimize for space/time complexity</strong> - This is especially useful when requesting code from GPT. For example, let's take the following prompt.

<blockquote><p><strong>Prompt: </strong>Write a Python script that iterates through a list of elements and removes duplicates.</p></blockquote>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_h2u09Xj.png" alt="GPT output of the above prompt"></figure>

It's very readable but not the fastest way you could do it in Python. Here is the prompt with that extra phrase added:

<blockquote><p><strong>Prompt:</strong> Write a Python script that iterates through a list of elements and removes duplicates. Optimize for time complexity.</p></blockquote>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_XzPquvh.png" alt="GPT output of the above prompt"></figure>

As you can see, you can get much quicker and cleaner code by letting GPT know what is essential to you.

## Tips for Summarizing Text

One of the strengths of GPT is summarizing text. Here are some ideas to make it even better. I'll use the Aesop fable, <i>The Fox and the Grapes</i>.

<strong>Write the key takeaways</strong> - I've found this to be even better than 'summarize' because it's not just regurgitating the passage but actually thinking about what is essential and what isn't

<strong>Construct 3 critical questions - </strong> Good way of making sure you understand the text.

<strong>Write a Twitter post/blog post </strong> \- It even provides the hashtags!

<strong>Create a Subject Line </strong> \- I've started using this to create titles for my blog posts!

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_ZguQqLR.png" alt="GPT output of the above prompt"></figure>

## Text Transformations

Text transformations are when you take an input text and generate new text. You've already seen a couple examples of this at work when we created a subject line and tweet for <i>The Fox and the Grapes</i>, but I'll share some more tangible examples of how I used a ton of text transformations in this blog post!

<blockquote><p><strong>Prompt:</strong> Generate a website slug for this blog post&nbsp;&nbsp;&nbsp;<br><strong>Reply: </strong>optimizing-gpt-for-nlp-tips-and-tricks</p><p><strong>Prompt:</strong> Give me a snippet summary for this blog post&nbsp;&nbsp;&nbsp;<br><strong>Reply:</strong> GPT is a powerful natural language processing tool that can be optimized for various tasks, such as text generation, code completion and text summarization. In this blog post, we will look at tips and tricks to get the most out of GPT.</p><p><strong>Prompt:</strong> Generate a title for this post&nbsp;&nbsp;&nbsp;<br><strong>Reply:</strong> "Tips and Tricks for Working with GPT: An Introduction to Optimizing GPT for Natural Language Processing"</p><p><strong>Prompt: </strong>Can you make it more concise?&nbsp;&nbsp;&nbsp;<br><strong>Reply: "</strong>Optimizing GPT for Natural Language Processing: Tips and Tricks"</p></blockquote>

## Custom Markup and Operators

If you get fancy with your prompts, you can 'teach' GPT new things! In the following examples, I use new operators like <code>=</code> and <code>!</code> along with additional markup in brackets <code>[ ]</code>, but the possibilities are endless. For example, Discord User @MasterWaffle is <a target="_blank" rel="noopener noreferrer" href="https://discord.com/channels/974519864045756446/1046656638150524989/1056006184982827098">developing a programming language using GPT (Discord Thread)</a>!

### Inline Dynamically Generated Values

It's possible to give GPT inline instructions by nesting them inside custom markup such as brackets. Here I'm using the verb <code>write:</code> to introduce some variety to the output.

<blockquote><p><strong>Prompt:</strong> Replace text enclosed in brackets that begins with "write:" with text that fits the description after "write:" Do not alter any other text. If you understand, reply with "Yes, Sir!".&nbsp;&nbsp;&nbsp;<br><strong>Reply: </strong>Yes, Sir!</p><p><strong>Prompt: </strong>A man went to [write:a USA state].&nbsp;&nbsp;&nbsp;<br><strong>Reply:</strong> A man went to California.</p><p><strong>Prompt: </strong>[write:a woman's name] went with [write:a man's name] to [write:a location].&nbsp;&nbsp;&nbsp;<br><strong>Reply:</strong> Alice went with Bob to the beach.</p></blockquote>

### Introduce a <code>=</code> Operator

In this example, we use <code>=</code> to tell GPT to tell us how it would answer each prompt differently. This can be useful to quickly try out two prompts to see which one you want to use.

<blockquote><p><strong>Prompt:</strong> If future input contains reference-marker:"=", then perform the following steps exactly and then write output else ignore.&nbsp;&nbsp;&nbsp;<br>1. compare both sides of the "=" sign, write a list of any ways you might handle one differently than the other if you where to respond to either. If you understand, reply with, "K" and do not say anything else.&nbsp;&nbsp;&nbsp;<br><strong>Reply: </strong>K</p><p><strong>Prompt: </strong>What is the best file format to use if I want to optimize for size and interoperability for aerial imagery? = What file format should I use if I have aerial imagery and I want it to be the most 'cloud optimized'?</p><p><strong>Reply:</strong> Some ways you might handle one differently than the other if you were to respond to either:</p><p>If you want to optimize for size, you might consider using a lossy file format like JPEG or JPEG2000, which can reduce the file size significantly without sacrificing too much image quality.&nbsp;&nbsp;&nbsp;<br>If you want to optimize for interoperability, you might consider using a more universally supported file format like TIFF or PNG, which can be easily opened by most software programs.&nbsp;&nbsp;&nbsp;<br>If you want to optimize for use in the cloud, you might consider using a file format that is well-suited for online storage and retrieval, such as Google's Cloud Optimized GeoTIFF (COG) format.</p></blockquote>

### Introduce a <code>!</code> Operator to create a Prompt Generator!

This is one version of a 'prompt optimizer' that uses a <code>!</code> to take any input and transform it into a more NLP-friendly prompt!

<blockquote><p><strong>Prompt: </strong>You will act as a NLP prompt generator. If future input starts with reference-marker:"!", then perform the following steps exactly and then write output else ignore:</p><p>START&nbsp;&nbsp;&nbsp;<br>1. For now, only acknowledge everything following this step as a template: "Example prompt with variables/conditions: "Please [write/speak] a [formal/informal] message to [audience] addressing the issue of [topic]. Be sure to convey a [positive/neutral/negative] tone and consider the [cultural/societal] context of your message." Additional details to consider in the template: - The format of the input (e.g. written text, spoken words, multimedia) - The length of the input - Any specific goals or objectives that the input is meant to achieve"&nbsp;&nbsp;&nbsp;<br>2. Extract a logically sound NLP structure from input, using the above step-by-step process to complete the defined role or task(s); fill out a prompt template using input.&nbsp;&nbsp;&nbsp;<br>END&nbsp;&nbsp;&nbsp;<br>If you understand, reply with "K."</p><p><strong>Reply: </strong>K</p><p><strong>Prompt:</strong> !Write a blog post about recursion for Python beginners.</p><p><strong>Reply:</strong> Example prompt with variables/conditions:</p><p>"Please write a blog post about recursion for Python beginners. The post should be written in a friendly, informative tone and should be suitable for readers who are new to programming. The post should cover the basics of recursion, including the definition of recursion, how it works, and how to implement it in Python. You should also include examples to help readers understand the concept and practice using it. The post should be at least 500 words long, and should include clear and concise explanations, as well as interactive examples that readers can try out on their own. The post should also include any relevant resources or links for further reading."</p></blockquote>

## GPT as a Prompt Generator (example 2)

I liked @MasterWaffel's example, so I tried my hand at my prompt optimizer. The idea is that you can give it a poor question, and it turns it into a good one!

<blockquote><p><strong>Prompt:</strong> I want you to act as a prompt optimizer. When I give you a prompt, evaluate, "How do I write a prompt for {prompt} using NLP."</p><p>Reply to the new prompt instead of the original. Provide as much detail as possible. List all of the important factors to consider.&nbsp;&nbsp;&nbsp;<br>Do not provide any explanations. Only include the new prompt.&nbsp;&nbsp;&nbsp;<br>If you understand, reply with, "K."</p><p><strong>Reply:</strong> K.</p><p><strong>Prompt: </strong>What is the best programming language?</p><p><strong>Reply: </strong>New Prompt: Compare the features of different programming languages to determine which one is the best for a specific purpose. Evaluate the language's syntax, readability, scalability, and support for various platforms. Consider the language's longevity, performance, and popularity among developers. Provide evidence to support your conclusion.</p></blockquote>

It works well, but I know there is much room to improve. I like the idea of creating a positive feedback loop where you can integrate with the model and continually improve prompts!

## Shorten Prompts to Stay Under Length Limits

When using <a target="_blank" rel="noopener noreferrer" href="https://platform.openai.com/">OpenAI's playground</a>, the length limits are the combined number of tokens in both the prompt and the response. This means that if you have a very long prompt, I will shorten the length of a reply. One clever way to combat this is to write your prompts using short-hand. Here I am instructing GPT to shorten the Preamble to the US Constitution. It appears to be removing the vowels, significantly reducing the number of characters (327/218 = 33% smaller!)

<blockquote><p><strong>Prompt: </strong>Take the following input, make it as few characters as physically possible with no information loss. Remove vowels when possible.&nbsp;<br>INPUT&nbsp;<br>&lt;copy/paste&gt;</p></blockquote>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_hbCNuZj.png" alt="GPT output of the above prompt"></figure>

To uncompress, simply ask GPT to bring it back! I have done this in a separate thread and multiple other examples, and it works every time!

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_mXWaXoB.png" alt="GPT output of the above prompt"></figure>

This way, you can simply submit the compressed version as a prompt, and GPT will expand it under the hood without impacting the total character count!

<h2 id="directives">Explore a Topic with Dynamic Inline Values (Directives)</h2>

I will admit calling these 'dynamic inline values' is totally made up, but I'm not sure what else to call them. They were explored a bit earlier, but I want to show them really shine when you are using GPT in an exploratory way like you would with a Jupyter Notebook.

<blockquote><p>A directive is a term used to tell GPT you are instructing it to do something. Directives, are written in a specific format and can include action verbs such as "write," "do," or "type." Directives may also include additional conditions that must be followed, indicated by a colon (:). GPT processes directives in the order they are written and can follow logical operations such as AND, OR, and XAND (which represents "not AND"). The general format looks like this:&nbsp;</p><p>[directiveName: directObject1...directObjectN]</p></blockquote>

Here is an example of a prompt with several directives.

<blockquote><p><strong>Prompt:</strong> The following will be a subject, [write: all categories and subcategories] and do not respond to text: &lt;subject&gt;</p></blockquote>

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_hQXKHaD.png" alt="GPT output of the above prompt"></figure>

As you can see, this is super powerful! Simply replace 'A game of Dungeons and Dragons' with whatever you want, and you'll get all the significant categorizations. I see this as applicable if you interact with GPT via its API.

## Conclusion

This blog post discussed some tips and techniques for using ChatGPT. By carefully adjusting GPT for specific purposes such as text generation, code completion, text summarization, and text transformation, you can fully utilize its capabilities and apply it to various challenges. Keep these strategies in mind as you work with ChatGPT to achieve the best outcomes.

If you have any ideas on how we can make this better, DM me on Twitter <a target="_blank" rel="noopener noreferrer" href="https://twitter.com/_jsolly">@_jsolly</a>
