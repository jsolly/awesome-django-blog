---
slug: migrating-to-postgres-from-sqllite
title: Migrating From SQLite to Postgres With Django - Documenting Gotchas
category: dev-tools
description: Migrate from SQLite to Postgres in Django with this step-by-step guide, including lessons learned and 'gotchas' encountered.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/upgrade_MOysw88.png
legacyImage: post_metaimgs/upgrade_MOysw88.png
imageAlt: Arrows pointing upward
imageAttribution: ""
imageWidth: 1920
imageHeight: 1280
published: "2022-03-07T13:22:13Z"
updated: "2026-09-07T14:25:05.450Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Migrate from SQLite to Postgres in Django with this step-by-step guide, including lessons learned and 'gotchas' encountered.</p>
legacyId: 17
related:
  - one-click-django-debug-runserver-livereload-chrome
  - how-to-setup-logging-in-your-django-app
  - use-brave-search-goggles-to-improve-web-searches
---

Fought a war with Django to migrate from sqlite to postgres. Documented the 'gotchas' I ran into in my latest video:

<figure class="media"><div data-oembed-url="https://www.youtube.com/embed/Y2g5nUnZpNc"><div style="position: relative; padding-bottom: 100%; height: 0; padding-bottom: 56.2493%;"><iframe src="https://www.youtube.com/embed/Y2g5nUnZpNc" style="position: absolute; width: 100%; height: 100%; top: 0; left: 0;" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen="" title="Video: Migrating From SQLite to Postgres With Django - Documenting Gotchas"></iframe></div></div></figure>

Why did I go through the effort to migrate everything from slqlite? To be honest, I didn't 'need' to use postgres. According to the <a target="_blank" rel="noopener noreferrer" href="https://sqlite.org/whentouse.html">sqllite documentation</a>, it's perfectly fine to use it for websites this like mine.

<blockquote><p>SQLite works great as the database engine for most low to medium traffic websites (which is to say, most websites). The amount of web traffic that SQLite can handle depends on how heavily the website uses its database. Generally speaking, any site that gets fewer than 100K hits/day should work fine with SQLite. The 100K hits/day figure is a conservative estimate, not a hard upper bound. SQLite has been demonstrated to work with 10 times that amount of traffic.</p></blockquote>

The goal of this site is to teach me how to design stable, scalable web applications that can handle large amounts of traffic. Blogthedata.com might not get over 100K hits/day, but it's very possible that my next position has me working on an application that experiences that kind of traffic volume.

Onward and upward!
