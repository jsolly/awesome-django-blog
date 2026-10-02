---
slug: write-tests-2x-faster-with-github-copilot
title: "AI Pair Programmers: Writing Tests With Github Copilot"
category: dev-tools
description: Learn how AI pair programmers like Github Copilot can assist with writing tests, providing an example of its use in a 2D spaceship game.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/robot.webp
legacyImage: post_metaimgs/robot.webp
imageAlt: A picture of a cartoon robot
imageAttribution: https://pixabay.com/vectors/robot-android-148989/
imageWidth: 654
imageHeight: 1080
published: "2022-10-08T18:01:14.339Z"
updated: "2022-10-08T18:01:14.339Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how AI pair programmers like Github Copilot can assist with writing tests, providing an example of its use in a 2D spaceship game.</p>
legacyId: 103
related:
  - test-strategy-no-existing-tests
  - two-weird-reasons-I-love-unit-tests
---

## Why use AI pair programmers?

I have been using <a target="_blank" rel="noopener noreferrer" href="https://github.com/features/copilot">Github Copilot</a> for a few months now and have been blown away at how helpful it is when writing tests. These tools get a lot of bad rap, but I suggest you try them before you knock it. Tests are a great place to start.

## Writing Tests for GeoAsteroids

I have this \[2D spaceship game\] I wrote in Typescript. It didn't have any tests, so I thought it would be an excellent place to try Copilot. 

### Test moveShip

The following function fires whenever the user presses the up arrow on their keyboard.

<pre><code class="language-typescript language-javascript">/**
 * Move ship based on its x and y velocity
 */
function moveShip(ship: Ship): void {

  ship.centroid = new Point(
    ship.centroid.x + ship.xv,
    ship.centroid.y + ship.yv,
  );
}</code></pre>

Copilot cleverly suggests the following test without me typing anything! It's exactly what I was going to write anyway.

<pre><code class="language-typescript">test.concurrent('Move Ship', () =&gt; {
  const testShip = new Ship();

  testShip.xv = 1;
  testShip.yv = 1;
  moveShip(testShip);
  expect(testShip.centroid.x).toBeGreaterThan(0);
  expect(testShip.centroid.y).toBeGreaterThan(0);
});</code></pre>

## Conclusion

AI pair programmers are not perfect. Sometimes the suggestions are flat-out wrong, and I am always weary of mindlessly accepting the autocomplete. But tools like Copilot already deliver great value for low-hanging fruit like writing tests. I am excited to continue using it and look forward to Copilot taking more and more off my plate. This way, I can focus on the most creative aspects of programming (writing new features!).
