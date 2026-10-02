---
slug: migrating-to-django-4x
title: "Upgrading to Django 4.0: Navigating Dependency and Migration Errors"
category: web-dev
description: Navigating dependency and migration errors while upgrading to Django 4.0 - A guide to upgrading from Django 3.2.14 to 4.0.5
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/django_support_timeline.jpg
legacyImage: post_metaimgs/django_support_timeline.jpg
imageAlt: Django support timeline. Shows 3.2 support ending in 2022.
imageAttribution: ""
imageWidth: 721
imageHeight: 336
published: "2022-06-09T02:34:50Z"
updated: "2026-09-07T14:25:05.480Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Navigating dependency and migration errors while upgrading to Django 4.0 - A guide to upgrading from Django 3.2.14 to 4.0.5</p>
legacyId: 63
related:
  - how-to-implement-content-security-policy-django
  - migrating-to-ckeditor-5
  - django-htmx-real-time-comments
---

<p style="margin-left:0px;">My friend Justin created an issue in my repo for migrating to Django 4.0. I couldn’t because a dependency, <a target="_blank" rel="noopener noreferrer" href="https://github.com/dmpayton/django-admin-honeypot">django-admin-honeypot</a>, and <a target="_blank" rel="noopener noreferrer" href="https://django-htmx.readthedocs.io/en/latest/installation.html">HTMX</a> did not work on 4.0. I made the leap after HTMX officially started advertising 4.0 support.</p>

<p style="margin-left:0px;">With <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/pull/105/commits/51116b5017ecd6b13dc505be0fcb9a92cbab759f">this PR</a>, I’ve migrated blogthedata.com to Django 4.0.5.</p>

<h2 style="margin-left:0px;"><strong>The upgrade</strong></h2>

<h3 style="margin-left:0px;"><strong>Startup Error</strong></h3>

<p style="margin-left:0px;">I followed my <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/upgrading-to-the-latest-3x-django/">upgrade document</a> and ran into my first issue; The app wouldn’t start! There was an error in the console:</p>

<pre><code class="language-python"> RuntimeError: populate() isn’t reentrant</code></pre>

<p style="margin-left:0px;">It’s an unhelpful Django error often due to a misconfigured dependency in settings.py. Someone mentioned in <a target="_blank" rel="noopener noreferrer" href="https://stackoverflow.com/questions/27093746/django-stops-working-with-runtimeerror-populate-isnt-reentrant/55929118#55929118">this SO thread</a> that a one-line change in <code>django/apps/</code><a target="_blank" rel="noopener noreferrer" href="https://app.prowritingaid.com/registry.py"><code>registry.py</code></a> surfaces the error.</p>

<p style="margin-left:0px;">Sure enough, the error was coming from a module <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/admin-honeypot-page-to-catch-hackers/">I incorporated in the past</a>.</p>

<pre><code class="language-python"> Could not import ugettext_lazy</code></pre>

<p style="margin-left:0px;">The <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/releases/4.0/">Django 4.0 upgrade doc</a> states that Django 4.0 removes this import.</p>

<p style="margin-left:0px;">I found an <a target="_blank" rel="noopener noreferrer" href="https://github.com/dmpayton/django-admin-honeypot/issues/87">open issue</a> in the django-admin-honeypot repo, but no one has actioned it for three months. My options were:</p>

<p style="margin-left:0px;">1 - Drop the package</p>

<p style="margin-left:0px;">2 - Patch it myself</p>

<p style="margin-left:0px;">3 - Find a replacement.</p>

<p style="margin-left:0px;">There are similar repos (<a target="_blank" rel="noopener noreferrer" href="https://github.com/jamesturk/django-honeypot/">1</a>, <a target="_blank" rel="noopener noreferrer" href="https://github.com/blag/django-admin-honeypot">2</a>), but these packages aren’t well maintained either. Additionally, re-work was required to change modules. I chose to eliminate the dependency. Although the functionality is interesting, it hasn’t caught any login attempts (who hacks a personal blog?).&nbsp;</p>

<h3 style="margin-left:0px;"><strong>Migration error</strong></h3>

<p style="margin-left:0px;">The app failed again but from a migration error. Migration, 0006_change_content_field_to_richtextuploading.py, imports the old django-ckeditor package I used when first implementing CKEditor.</p>

<p style="margin-left:0px;">I saw <a target="_blank" rel="noopener noreferrer" href="https://code.djangoproject.com/ticket/25327">this ticket</a> in the official Django repo, where a commenter suggests <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/dev/topics/migrations/#migration-squashing">migration squashing</a>. Squash migrations reduce the number of migrations by ‘squashing’ them into one file.</p>

<pre><code class="language-python">$ python3 manage.py squashmigrations blog 0006                                             
Will squash the following migrations:
 - 0001_initial
 - 0002_add_likes
 - 0003_add_views_to_Post
 - 0004_add_slug_field
 - 0005_add_images_to_post
 - 0006_change_content_field_to_richtextuploading
Do you wish to proceed? [yN] </code></pre>

<p style="margin-left:0px;">Typed ‘Y’ and hit enter</p>

<pre><code class="language-python">Created new squashed migration /Users/johnsolly/Documents/code/blogthedata/django_project/blog/migrations/0001_squashed_0006_change_content_field_to_richtextuploading.py
  You should commit this migration but leave the old ones in place;
  the new migration will be used for new installs. Once you are sure
  all instances of the codebase have applied the migrations you squashed,
  you can delete them.</code></pre>

<p style="margin-left:0px;">I followed the instructions, and everything started working again!&nbsp;</p>

<h2 style="margin-left:0px;"><strong>Conclusion</strong></h2>

<p style="margin-left:0px;">I ran into two errors during the upgrade from Django 3.2.14 to 4.0.5. The first was a third-party dependency not supported on 4.0. A second issue was a migration error from a removed dependency. The missing import was resolved by eliminating a dependency. The second issue was addressed by squashing migrations.</p>

<p style="margin-left:0px;">I am excited to now use Django 4.0!</p>
