---
slug: integration-tests-are-a-scam-i-wrote-them-anyway
title: "Breaking Up With Integration Tests: Switch To Collab & Contract Tests"
category: dev-tools
description: Are integration tests a scam? Find out why J.B Rainsberger believes so and learn how to move away from integration tests toward collaboration and contract tests
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/selenium_python.jpg
legacyImage: post_metaimgs/selenium_python.jpg
imageAlt: The selenium and python logos next to each other.
imageAttribution: ""
imageWidth: 1600
imageHeight: 899
published: "2022-04-13T03:10:10Z"
updated: "2024-11-06T13:34:39.057Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Are integration tests a scam? Find out why J.B Rainsberger believes so and learn how to move away from integration tests toward collaboration and contract tests</p>
legacyId: 35
related:
  - two-weird-reasons-I-love-unit-tests
  - test-strategy-no-existing-tests
---

According to J. B. Rainsberger, <a target="_blank" rel="noopener noreferrer" href="https://vimeo.com/80533536">integration tests are a scam</a> because of combinatorial complexity and a tendency to create MORE bugs. Complicated tests involving multiple units beget poor design, whereas tiny, isolated tests, are resilient and put pressure on our designs to make them better.

<a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-100-percent-unit-test-coverage/">Four days ago</a>, I achieved 100% unit test coverage. Today, I finished <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/pull/38/files">adding over 300 lines of code</a> of functional UI tests for blogthedata.com. After watching Rainsberger's talk, maybe I should drop them?

<blockquote><p>Integration tests is any test where the success or failure depends on many bits of interesting behavior at once…where when it fails, I cannot point to where the problem is.</p><p>J.B Rainsberger</p></blockquote>

Rainsberger advocates for <a target="_blank" rel="noopener noreferrer" href="https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)">hexagonal architecture</a> where different parts of the system are checked in isolation. Instead of integration tests, you write collaboration and contract tests to validate functions interact with interfaces correctly.

<strong>Collaborations Tests</strong>

<ul><li>Do I ask the server the right questions?</li><li>Can I handle all the answers the server gives me?</li></ul>

<strong>Contract Tests</strong>

<ul><li>What questions can I answer?</li><li>Do I really try to answer that way?&nbsp;</li></ul>

Collaboration tests are about whether senders and receivers can understand each other's questions and answers. Contract tests are about whether the type and content of each question and answer conform to an established standard. 

What's fantastic about this approach is that the client and server are tested independently. By using stubs and mocks, you can turn what would otherwise be an integration test into a unit test!

As I develop blogthedata.com, I will migrate away from integration toward collaboration and contract.
