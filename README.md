[![blogthedata-tests](https://github.com/jsolly/blogthedata/actions/workflows/django-test.yaml/badge.svg)](https://github.com/jsolly/blogthedata/actions/workflows/django-test.yaml)
![Coverage](https://img.shields.io/coverallsCoverage/github/jsolly/blogthedata)
![CodeStyle](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Python Version](https://img.shields.io/badge/python-3.10-brightgreen.svg)](https://www.python.org/downloads/)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)
# blogthedata.com

Welcome to my Django blog app! This app is a fully functional blogging platform that I built using the Django web framework. It includes features such as creating and managing blog posts, comments, and categories, as well as user authentication and authorization. The app is designed to be easily integrated into any existing Django project or can be used as a standalone app. In this readme, you will find instructions for installation, configuration, and usage that I have provided. I have also included information about the app's features and troubleshooting tips that I have gathered. I hope you find this app useful and I welcome any contributions or suggestions for improvement.

![LighthouseScore](https://github.com/jsolly/jsolly/blob/main/assets/lighthouseStats.svg)

![desktopScreenshot](https://user-images.githubusercontent.com/9572232/183277781-adea9d73-6dc0-4971-ac3a-b14e2131d6f3.jpeg)

---

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)

## Installation

```shell
# first install Python 3.10.x (have not tested newer versions, but they could work)
$ git clone https://github.com/jsolly/blogthedata.git
$ python3 -m venv blogthedata/django_project/venv
$ source blogthedata/django_project/venv/bin/activate
$ pip install --upgrade pip
$ python3 -m pip install -r blogthedata/django_project/requirements/requirements.txt -c blogthedata/django_project/requirements/constraints.txt
```

## Setup

### Database

1. See commented out Database section in
   [django_project/settings/dev.py](https://github.com/jsolly/blogthedata/blob/master/django_project/django_project/settings/dev.py)
   to use sqllite database or postgres. If you're on MacOS, there's a really handy app called [postgres.app](https://postgresapp.com/)

```shell
$ sudo -U postgres psql
postgres=# CREATE USER blogthedatauser WITH PASSWORD 'password';
postgres=# ALTER ROLE blogthedatauser SET client_encoding TO 'utf8';
postgres=# ALTER ROLE blogthedatauser SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE blogthedatauser SET timezone TO 'UTC';
postgres=# CREATE DATABASE blogthedata WITH OWNER blogthedatauser;
postgres=# \c blogthedata
postgres=# CREATE extension postgis;
postgres=# SELECT PostGIS_version();
# type <exit> and hit enter to go back to the terminal
$ python3 manage.py migrate
```

2. rename 'sample.env' to .env and change the values to match your setup
   (database passwords, secret keys, etc)

```shell
$ python3 manage.py runserver
```

### Coverage

```shell
$ coverage run -m pytest django_project
$ coverage report -m --skip-covered
```

### Test

```shell
$ psql -U postgres
postgres=# CREATE DATABASE blogthedata_test WITH OWNER blogthedatauser;
postgres=# \c blogthedata_test
postgres=# CREATE extension postgis;
postgres=# SELECT PostGIS_version();
# type <exit> and hit enter to go back to the terminal
$ python3 blogthedata/django_project/manage.py migrate
$ python3 -m pytest django_project
```

### Lint

```shell
$ flake8 django_project
```

Also see the [actions tab](https://github.com/jsolly/blogthedata/actions)
to see if everything is passing.

### Pre-commit Hooks (Optional as the CI also takes care of it)

```
$ cd blogthedata
$ chmod +x run_tests.sh
$ pre-commit install
```

### Local server (For mobile testing)

[Use Ngrok](https://ngrok.com/)

---

## Features

### Functional Features

- User login (header links removed in
  [commit:5c050a5b68d9c8ce7dcf90fdef44377cc28eab6b](https://github.com/jsolly/blogthedata/commit/5c050a5b68d9c8ce7dcf90fdef44377cc28eab6b))
- Create posts filtered by category or author
- Create Comments (Removed in https://github.com/jsolly/blogthedata/pull/77)
- User profile with avatar (automatic sizing and compression using Pillow)
- Ckeditor 5 for authoring blog posts (also includes spell check, code snippets, character
  counter, and more!)
- Post views and likes (Removed in
  https://github.com/jsolly/blogthedata/pull/77)
- Newsletter Sign up 🗞 (removed in https://github.com/jsolly/blogthedata/pull/140)
- Github Integration to show active issue backlog without leaving blog (removed
  in https://github.com/jsolly/blogthedata/pull/121)
- Slugified URLs for more readable links
- Open Graph protocol compliant social media sharing for beautiful share cards (LinkedIn, Twitter, Facebook, Instagram, Reddit, etc)
- Smart and powerful Global search so you can find any blog post with a keyword search.
- Ko-Fi donation button ☕️ (removed in https://github.com/jsolly/blogthedata/commit/c857bb7599836c614aff523756bbf1381e0dd948)
- Leaflet.js and OpenLayers maps 🗺
- Display site visitors in a web map
- Portfolio page with testimonials, contact me, Web vitals, and more!
- Light and Dark Theme
- Blog reading time so viewers can estimate how long it will take them to read a post.
- Atom and RSS feed so users can subscribe to your latest blog posts.
- GPT3 powered blog post title, slug, and metadesc generator so you can harness the power of AI in your blog post authoring workflow
- Copy to clipboard links on every header within a blog post so you can share specific sections of a post.
- Site-wide 'breadcumbs' so your users can know exactly where they are and navigate with ease.

### Non-Functional Features

- Robots.txt, security.txt, and sitemap.xml for optimized SEO and security
- Honeypot Admin page to automatically block IPs trying to login with an admin account (Removed in
  https://github.com/jsolly/blogthedata/pull/105)
- Git hooks for automatic static file generation (manage.py collectstatic)
- GitActions CI integration with coverage, linting, and testing. Push with confidence!
- Latest Bootstrap 5.x
- Compatible with Sqllite or postgres databases for fast protyping and production
- Optimized for Performance, SEO, and A11Y
- Latest Django 4.x
- 95% or above unit code coverage for a maintainable codebase
- 100% linted with [flake8](<[url](https://pypi.org/project/flake8/)>) and PEP8 compliant\* for beautiful Python code.
- Static scans with [CodeQL](<[url](https://codeql.github.com/)>) and pip
  dependency checks with [Dependabot](<[url](https://github.com/dependabot)>) for automated security and updates.
- Formatted with [Black](<[url](https://pypi.org/project/black/)>) for beauty and readability
- Strict Content Security Policy preventing inline styles and scripts for better security
- Subresource Integrity for better security
- [A+ Score on Mozilla Observatory](<[url](https://observatory.mozilla.org/analyze/blogthedata.com)>)
- 100/100 for Performance, SEO, and Accessibility according to Google Lighthouse
- Custom 404 page that looks really cool. So even if your users are lost, they are still having a good time.
- Automatic Conversion of images (.png, .jpeg, etc) to .webp for blazingly fast image loads.

---

## Contributing

Want to work on this with me? DM me
<a href="https://twitter.com/_jsolly" rel="noopener noreferrer" target="_blank">
`@_jsolly`</a>

### Step 1

- **Option 1**

  - 🍴 Fork this repo!

- **Option 2**
  - 👯 Clone to your local machine using:
    `https://github.com/jsolly/blogthedata.git`

### Step 2

- **HACK AWAY!** 🔨🔨🔨

### Step 3

- 🔃 Create a new pull request using:
  <a href="https://github.com/jsolly/blogthedata/compare" rel="noopener noreferrer" target="_blank">
  `https://github.com/jsolly/blogthedata/compare`</a>.

---

## Team

|                                               John Solly                                               |
| :----------------------------------------------------------------------------------------------------: |
|   [![jsolly](https://avatars1.githubusercontent.com/u/9572232?v=3&s=200)](https://github.com/jsolly)   |
| <a href="https://github.com/jsolly" rel="noopener noreferrer" target="_blank"> `github.com/jsolly`</a> |

---

## Support

Reach out to me at one of the following places!

- Twitter -
  <a href="https://twitter.com/_jsolly" rel="noopener noreferrer" target="_blank">
  `@_jsolly`</a>

---

## Donations

<a href='https://ko-fi.com/S6S6CSR2Q' rel="noopener noreferrer" target='_blank'><img height='36' style='border:0px;height:36px;' src='https://cdn.ko-fi.com/cdn/kofi2.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com'></a>

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
