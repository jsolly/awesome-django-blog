---
slug: I-re-created-1979-Atari-game-asteroids-with-JS
title: "GeoAsteroids: Refactoring a JS Asteroids Clone Into a GIS Game"
category: Geodev
description: I've refactored my JavaScript Asteroids clone into a modular application and made it into a game for GIS nerds. Check out GeoAsteroids.com to play!
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/GeoAsteroids_screenshot.png
legacyImage: post_metaimgs/GeoAsteroids_screenshot.png
imageAlt: Screenshot of GeoAsteroids
imageAttribution: ""
imageWidth: 800
imageHeight: 621
published: "2022-07-11T03:58:49Z"
updated: "2026-09-07T14:25:05.486Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>I've refactored my JavaScript Asteroids clone into a modular application and made it into a game for GIS nerds. Check out GeoAsteroids.com to play!</p>
legacyId: 73
related:
  - sollys-favorite-web-resources-and-tools
  - how-I-present-portfolio-projects-to-impress
---

After spending the last few months with Python and Django, I thought of a project to help sharpen my JavaScript skills. I found <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/watch?v=H9CSWMxJx84">this Youtube Tutorial</a> where you re-create Asteroids in 2 hours and 45 mins. After completing the tutorial, the whole app becomes a <a target="_blank" rel="noopener noreferrer" href="https://drive.google.com/file/d/1tmjvMKxCcJeyTpi5pI6A8cgVxwWnyPXn/view">single HTML file</a> with a \<script\> that is about ~1000K lines long.

I wanted the application to be more modular, so I split it into 10 files <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoAsteroids/pull/3/files">in this PR</a>. I think it looks and reads A LOT better. Instead of the code being one long file, I have separated out logic such as collisions, scoring, and sound effects. This way, adding new features will be much easier, and it's less of a maintenance nightmare. 

My goal for the project is to make it into a game for GIS nerds like me. You'll be able to upload your geospatial data and play the game with YOUR polygons. 

Stay tuned for more updates. If you want to log a bug/enhancements, check out <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoAsteroids">GeoAsteroid's Github repo</a>.

The game is live at <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/GeoRoids">GeoAsteroids.com</a>
