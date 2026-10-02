---
slug: Prettier-code-formatter-breaks-Django-templates
title: Why You Shouldn't Use Prettier on Django Template Files
category: dev-tools
description: "Don't use Prettier on Django Templates: My Experience and Why it's Not Compatible with the Template Language's Syntax"
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/prettierLogo.webp
legacyImage: post_metaimgs/prettierLogo.webp
imageAlt: Prettier Logo with a red x over it
imageAttribution: https://raw.githubusercontent.com/prettier/prettier-logo/master/images/prettier-banner-dark.png
imageWidth: 300
imageHeight: 300
published: "2022-08-03T19:39:58.281Z"
updated: "2022-08-03T19:39:58.281Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: "<p>Don't use Prettier on Django Templates: My Experience and Why it's Not Compatible with the Template Language's Syntax</p>"
legacyId: 94
related:
  - upgrading-to-the-latest-3x-django
  - how-to-get-a-perfect-mozilla-observatory-score
  - mastering-intuition-pumps-essential-terms-guide
---

I recently tried prettier out on HTML files in my project. Unfortunately, it tends to break Django template code and <a target="_blank" rel="noopener noreferrer" href="https://github.com/prettier/prettier/issues/5581">Prettier doesn't intend to fix it</a>. Makes sense as it's tricky that Python is whitespace sensitive and Prettier's userbase is mainly JS devs.

Django devs beware! Don't use prettier if you use Django's templating engine!!!!
