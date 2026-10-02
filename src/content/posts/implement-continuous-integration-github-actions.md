---
slug: implement-continuous-integration-github-actions
title: "Adding CI to Your Project: Setting Up Github Actions for Blogthedata"
category: dev-tools
description: Learn how to add a CI workflow to your project with Github Actions. A step-by-step guide to test, lint, and deploy code with Github Actions.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/CI_Workflow.png
legacyImage: post_metaimgs/CI_Workflow.png
imageAlt: Code, Build, Test, Release, Deploy, Operate, Monitor,  Plan.
imageAttribution: https://cdn-images-1.medium.com/max/1600/1*TNJ7Rpr5G1OJHtKH-IBEFw.png
imageWidth: 1600
imageHeight: 639
published: "2022-05-16T02:42:45Z"
updated: "2026-09-07T14:25:05.476Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Learn how to add a CI workflow to your project with Github Actions. A step-by-step guide to test, lint, and deploy code with Github Actions.</p>
legacyId: 46
related:
  - Adding-views-likes-to-posts
  - how-to-test-and-debug-django-templates
  - code-analysis-and-pip-dependency-check-in-GitHub
---

## Note

Since writing this post, I moved to using <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/ruff/0.0.47/">Ruff </a> for Python linting.

## Intro

<a target="_blank" rel="noopener noreferrer" href="https://github.com/features/actions">Github Actions</a> test and lint all code changes before they are pushed into a branch. You can see this ‘in-action' on the <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/actions">actions tab of the blogthedata repo.</a> Actions can be added to any repo by placing a .yaml into the root directory.

<pre><code class="language-yaml">name: Blogthedata Tests
on:
  push:
  pull_request:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      SECRET_KEY: ${{secrets.SECRET_KEY}}
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python 3.9.7
      uses: actions/setup-python@v2
      with:
        python-version: 3.9.7
    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install wheel
        pip install -r config/requirements.txt
    - name: Lint with Flake8
      run: |
        flake8 django_project
    - name: Coverage + run unit tests
      run: |
 		coverage run -m pytest django_project
        coverage report -m --skip-empty --skip-covered</code></pre>

<strong>Lines 2 - 6</strong> - Specify the action trigger. I run the workflow whenever I attempt a push or PR with master as the target branch.

<strong>Lines 7 - 9</strong> - Spin up an Ubuntu container

<strong>Lines 10 - 11</strong> Set environment variables to be used by the container. These contain things like Django's SECRET\_KEY and any other sensitive tokens. When you use the {{secrets.\<name\>}} syntax, you’re accessing <a target="_blank" rel="noopener noreferrer" href="https://docs.github.com/en/actions/security-guides/encrypted-secrets"> encrypted secrets</a> set within your repo's settings page. This actually forced me to change my implementation because I was loading secrets with a configuration file not committed to source control. I switched to environment variables because that appeared to be easier and safer to use with Github Actions.

<strong>Line 13</strong> - Check out code from the <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata">blogthedata repo</a>

<strong>Lines 14 - 22</strong> - Install Python and its dependencies within the Ubuntu container created on <strong>line 9</strong>

<strong>Lines 23 - 25</strong> - Lint the code using <a target="_blank" rel="noopener noreferrer" href="https://flake8.pycqa.org/en/latest/">flake8</a>. Flake8’s configuration is stored in a .flake8 file. I exclude the Python virtual environment (venv), and db migrations from being linted. On the ignore line, I tell Flake8 to disregard <a target="_blank" rel="noopener noreferrer" href="https://www.flake8rules.com/rules/E501.html">E501, Line too long</a>

<pre><code class="language-bash">[flake8]
exclude = venv migrations
ignore = E501</code></pre>

<strong>Lines 26 - 29</strong> - Run code coverage using the <a target="_blank" rel="noopener noreferrer" href="https://coverage.readthedocs.io/en/6.3.3/">coverage module</a> <a target="_blank"> and unit tests with </a> <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/pytest/">PyTest</a>. I store the configuration in a <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/blogthedata/blob/master/config/.coveragerc">.coveragerc</a> file. The configuration loads the <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/django-coverage/">django-coverage</a> plugin which I talk more about in my post about <a target="_blank" rel="noopener noreferrer" href="https://blogthedata.com/post/how-to-get-perfect-linting-compliance/">how to get perfect PEP 8 compliance</a>. It also excludes test files from coverage..it's a little overkill to have unit tests for my unit tests! 

<pre><code class="language-bash">[run]
plugins = django_coverage_plugin
omit = 
    */tests/*</code></pre>

## Conclusion

The whole process takes about 2 minutes from start to finish. One way I could speed this up is by implementing mocks and stubs instead of relying on a database to complete unit tests.

A week ago, I had never used Github Actions and was simply trying to close this issue. My next step is to develop a CD (Continuous Deployment) workflow where production updates without any manual intervention. Today, I perform these three steps to update prod.

<ol><li>SSH into the production server</li><li>Perform a git pull to get the latest code</li><li>Restart Apache2 web server</li></ol>

It's not cumbersome, but it's good practice to automate, as anything done manually is prone to human error. You can track blogthedata.com CD progress in this issue.

Add a CI workflow to your project, today!
