---
slug: code-analysis-and-pip-dependency-check-in-GitHub
title: Automate Security in Your CI Workflow With CodeQL and Dependabot
category: dev-tools
description: Integrate CodeQL and Dependabot for automated security checks in your CI/CD workflow. Learn how to streamline your process and secure your codebase.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/CodeQL_and_dependabot.png
legacyImage: post_metaimgs/CodeQL_and_dependabot.png
imageAlt: Screenshot of CodeQL and Dependabot YAML code
imageAttribution: ""
imageWidth: 1316
imageHeight: 708
published: "2022-06-06T01:34:56Z"
updated: "2024-11-06T13:36:05.671Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Integrate CodeQL and Dependabot for automated security checks in your CI/CD workflow. Learn how to streamline your process and secure your codebase.</p>
legacyId: 62
related:
  - upgrading-to-the-latest-3x-django
  - implement-continuous-integration-github-actions
  - how-to-test-and-debug-django-templates
---

<blockquote><p>CodeQL is the analysis engine used by developers to automate security checks, and by security researchers to perform variant analysis.</p><p>In CodeQL, code is treated like data. Security vulnerabilities, bugs, and other errors are modeled as queries that can be executed against databases extracted from code. You can run the standard CodeQL queries, written by GitHub researchers and community contributors, or write your own to use in custom analyses. Queries that find potential bugs highlight the result directly in the source file.</p><p>-<a target="_blank" rel="noopener noreferrer" href="https://codeql.github.com/docs/codeql-overview/about-codeql/">CodeQL doc</a></p></blockquote>

<blockquote><p>Dependabot takes the effort out of maintaining your dependencies. You can use it to ensure that your repository automatically keeps up with the latest releases of the packages and applications it depends on.</p><p>-<a target="_blank" rel="noopener noreferrer" href="https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates">Dependabot Doc</a></p></blockquote>

After setting up CodeQL, it creates a new workflow inside .github/workflows. The default setup is to run static code analysis whenever a PR/push is made against the master branch. The problem was that two workflows executed each code push.

<figure class="image image_resized" style="width:81.27%;"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_8nDUbmE.png" alt="Screenshot of Git Actions showing two workflows. One by blogthedata tests and the other by CodeQL."></figure>

It made more sense for CodeQL to be the last step in my existing CI workflow instead of having to rebuild the container twice. I joined the two workflows.

<pre><code class="language-yaml">name: Blogthedata Tests
on:
  push:
  pull_request:
    branches:
      - main
  schedule:
    - cron: '0 3 * * 0-6'
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'javascript', 'python' ]
        # CodeQL supports [ 'cpp', 'csharp', 'go', 'java', 'javascript', 'python', 'ruby' ]
        # Learn more about CodeQL language support at https://aka.ms/codeql-docs/language-support

    env:
      DJANGO_SETTINGS_MODULE: ${{secrets.DJANGO_SETTINGS_MODULE}}
      SECRET_KEY: ${{secrets.SECRET_KEY}}
      EMAIL_HOST_USER: ${{secrets.EMAIL_HOST_USER}}
      EMAIL_HOST_PASSWORD: ${{secrets.EMAIL_HOST_PASSWORD}}
      FROM_EMAIL: ${{secrets.FROM_EMAIL}}
      ALLOWED_HOSTS: ${{secrets.ALLOWED_HOSTS}}
      POSTGRES_PASS: $${{secrets.POSTGRES_PASS}}
      GIT_TOKEN: ${{secrets.GIT_TOKEN}}
      DEBUG: ${{secrets.DEBUG}}
      MODE: ${{secrets.MODE}}
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
        pip install -r django_project/requirements/requirements.txt
    - name: Lint with Flake8
      run: |
        flake8 django_project
    - name: Coverage report
      run: |
        coverage run -m unittest discover django_project 
        coverage report -m --skip-empty --skip-covered
    - name: Run unit tests
      run: |
        python3 -m unittest discover django_project

    # Initializes the CodeQL tools for scanning.
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}
        # If you wish to specify custom queries, you can do so here or in a config file.
        # By default, queries listed here will override any specified in a config file.
        # Prefix the list here with "+" to use these queries and those in the config file.
        
        # Details on CodeQL's query packs refer to : https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/configuring-code-scanning#using-queries-in-ql-packs
        # queries: security-extended,security-and-quality

        
    # Autobuild attempts to build any compiled languages  (C/C++, C#, or Java).
    # If this step fails, then you should remove it and run the build manually (see below)
    #- name: Autobuild
    #  uses: github/codeql-action/autobuild@v2

    # ℹ️ Command-line programs to run using the OS shell.
    # 📚 See https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsrun

    #   If the Autobuild fails above, remove it and uncomment the following three lines. 
    #   modify them (or add more) to build your code if your project, please refer to the EXAMPLE below for guidance.

    # - run: |
    #   echo "Run, Build Application using script"
    #   ./location_of_script_within_repo/buildscript.sh

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2</code></pre>

The new code starts on <strong>line 58</strong>. I commented out <strong> lines 72 and 73</strong> because Python and JavaScript do not compile. CodeQL adds a few minutes to build time, including unit test coverage, linting, passing unit tests, and a security scan.

## Dependabot 

To add Dependabot, I <a target="_blank" rel="noopener noreferrer" href="https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file">created a dependabot.yml file</a> inside the .github folder.

<p style="margin-left:0.0px;">.github</p>

<p style="margin-left:0.0px;">├── dependabot.yml</p>

<p style="margin-left:0.0px;">└── workflows</p>

<p style="margin-left:0.0px;">&nbsp; &nbsp; └── django-test.yaml</p>

<pre><code class="language-yaml"># .github/dependabot.yml
# To get started with Dependabot version updates, you'll need to specify which
# package ecosystems to update and where the package manifests are located.
# Please see the documentation for all configuration options:
# https://docs.github.com/github/administering-a-repository/configuration-options-for-dependency-updates

version: 2
updates:
  # Maintain dependencies for GitHub Actions
  - package-ecosystem: "" # See documentation for possible values
    directory: "/" # Location of package manifests
    schedule:
      interval: "daily"


  # Maintain dependencies for pip package manager
  - package-ecosystem: "pip"
    directory: "/config/requirements.txt"
    schedule:
      interval: "daily"</code></pre>

I changed <strong> line 18</strong> to point it to my requirements.txt file. Dependabot creates PRs for the issues it finds. I have four open Dependabot branches that I'll tackle in <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/issues/101">this issue</a>. The code changes Dependabot suggests often bump the module version number in the requirements.txt. Since unit tests pass, I'll merge them and roll back if things go sideways.

<img class="image_resized" style="width:82.17%;" src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_OyvV6v2.png" alt="Screenshot of Dependabot PR. Code change from Pillow8.3.2 to 9.0.1"> 

## Conclusion

I lint, assess code coverage, run unit tests, and security scan my code + dependencies with two short YAML files. It takes 7-8 minutes for the CI workflow to finish, and dependabot creates PRs to fix vulnerabilities. My next step is to fix the <a target="_blank" rel="noopener noreferrer" href="https://github.com/jsolly/awesome-django-blog/issues/101">issues that were found</a>. Add CodeQL and Dependabot to your repo today!
