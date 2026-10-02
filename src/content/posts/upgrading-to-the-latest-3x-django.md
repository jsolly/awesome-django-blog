---
slug: upgrading-to-the-latest-3x-django
title: Upgrading to the Latest Django 3.x
category: web-dev
description: As a prerequisite to an upgrade to Django 4.0, I walk you through my upgrade process to the latest 3.x version
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/upgrade.png
legacyImage: post_metaimgs/upgrade.png
imageAlt: The text 'upgrade' with lots of arrows pointing upward
imageAttribution: ""
imageWidth: 1920
imageHeight: 1280
published: "2022-05-04T12:31:30Z"
updated: "2024-11-06T13:34:04.584Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>As a prerequisite to an upgrade to Django 4.0, I walk you through my upgrade process to the latest 3.x version</p>
legacyId: 37
related:
  - why-I-stopped-using-pip-freeze
  - implement-continuous-integration-github-actions
  - Adding-views-likes-to-posts
---

Django puts out a <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/howto/upgrade-version/">fantastic doc</a> on upgrading to the latest version. I am using Django 3.2.7 and the latest is  3.2.13. I follow a process instead of blindly upgrading to <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/migrating-bs4-to-bs5/">upgrade from Bootstrap 4 to 5</a>.

## Review Release Notes

I read the release notes for versions between my current version and the latest. For me that’s 3.2.8-\>3.2.9-\>3.2.10-\>3.2.11\>3.2.12\>3.2.13. I see nothing stand out that would break my app. I’m fortunate this is not a large version jump (like 3.x to 4.x) which comes with depreciations and breaking changes. There's currently <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/issues/37">an open issue</a> to do this major version upgrade on blogthedata.com

## Resolve depreciation warnings and run unit tests

According to the docs:

<blockquote><p>Before upgrading, it’s a good idea to resolve any deprecation warnings raised by your project while using your current version of Django. Fixing these warnings before upgrading ensures that you’re informed about areas of the code that need altering.</p><p>In Python, deprecation warnings are silenced by default. You must turn them on using the&nbsp;<code>-Wa</code>&nbsp;Python command line option or the&nbsp;<a target="_blank" rel="noopener noreferrer" href="https://docs.python.org/3/using/cmdline.html#envvar-PYTHONWARNINGS" title="(in Python v3.10)"><code>PYTHONWARNINGS</code></a>&nbsp;environment variable. For example, to show warnings while running tests:</p></blockquote>

When I ran the tests, everything looked wonderful except for depreciation warnings within the django-admin-honeypot module. I don’t worry because the error targets Django 4.0, not 3.x

<pre><code class="language-python">/code/blogthedata/django_project/venv/lib/python3.9/site-packages/admin_honeypot/admin.py:31: RemovedInDjango40Warning: django.utils.translation.ugettext_lazy() is deprecated in favor of django.utils.translation.gettext_lazy().
  get_path.short_description = _('URL')</code></pre>

A quick note on Python dependencies...there's a chance some Python modules will break in the latest Django version that won't show up in the depreciation warnings. Unfortunately, I don’t know how to test dependencies premetively. According to this <a target="_blank" rel="noopener noreferrer" href="https://stackoverflow.com/questions/43828874/how-to-update-packages-after-upgrading-django">SO thread</a>, you basically upgrade and see what happens with the stack traces.

## Backup Dependencies

The app running on my local machine in a virtualenv. To take a snapshot of dependencies, I run pip freeze to save them to a requirements.txt file. This file can be used to re-create the virtualenv if things go sideways.

<code>pip freeze &gt; requirements_5_4_22.txt</code>

## Perform the Upgrade in the Dev Environment

<code>pip install Django==3.2.13</code>

I re-ran my unit tests and everything passed!

## Perform the Upgrade in Prod

First I <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/commit/c26af01cd34563e508e465f5e8cdc3462b3345bc">commit the requirements file</a> to source control. Then I use it to upgrade Django in production.

Everything went smoothly! Prod is now on the latest 3.x Django version!
