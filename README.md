# Awesome Django Blog

[![awesome-django-blog-tests](https://github.com/jsolly/awesome-django-blog/actions/workflows/django-test-deploy-master.yaml/badge.svg)](https://github.com/jsolly/awesome-django-blog/actions/workflows/django-test-deploy-master.yaml)
[![Coverage Status](https://coveralls.io/repos/github/jsolly/awesome-django-blog/badge.svg?branch=master&service=github)](https://coveralls.io/github/jsolly/awesome-django-blog?branch=master)
![CodeStyle](https://img.shields.io/badge/code%20style-black-000000.svg)
![Linting](https://img.shields.io/badge/linting-ruff-orange)
[![Python Version](https://img.shields.io/badge/python-3.10-brightgreen.svg)](https://www.python.org/downloads/)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

Awesome-django-blog is a fully functional blogging platform built using the Django web framework. It includes features such as creating and managing blog posts, comments, and categories, as well as user authentication and authorization.

![desktopScreenshot](https://user-images.githubusercontent.com/9572232/183277781-adea9d73-6dc0-4971-ac3a-b14e2131d6f3.jpeg)

---

## Table of Contents

- [Installation](#installation)
- [Development](#development)
- [Features](#features)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

## Installation

```shell
# first install Python 3.10.x (have not tested newer versions, but they could work)
git clone https://github.com/jsolly/awesome-django-blog.git
cd awesome-django-blog
python3 -m venv .venv
source .venv/bin/activate
# You only need requirments.txt on production
pip install --upgrade pip && pip install -r requirements.txt
python3 app/manage.py migrate
python3 app/manage.py createsuperuser # optional to create a user who can create posts and comments
```

Rename 'awesome-django-blog/sample.env' to .env and change the values to match your setup. 
            (database passwords, secret keys, etc)

By default USE_SQLITE is set to `True` if you want to use something else like postgres, set this to False and modify the DJANGO_DB_SETTINGS variable in the file.

```shell
cd awesome-django-blog/app
python3 manage.py runserver
```

### Configure Django Sites Framework

1 - Run the server and navigate to http://127.0.0.1:8000/admin/sites

2 - Add a new site with the following values: - Domain name: 127.0.0.1:8000 - Display name: 127.0.0.1:8000

Here is a screenshot of my sites configuration:

3 - Now go into your settings.dev file and change the SITE_ID to the ID of the site you just created. It should be 1 if you have yet to create any other sites.


## Installation (Docker)

```shell
git clone https://github.com/jsolly/awesome-django-blog.git
cd awesome-django-blog
docker-compose build
docker-compose run --rm app sh -c "python manage.py createsuperuser"
docker-compose up
```


### Coverage

```shell
coverage run --rcfile=config/.coveragerc -m pytest app
coverage report -m --skip-covered --rcfile=config/.coveragerc
```

### Tests

```shell
pytest app
```

### Linting

```shell
ruff --config ./config/pyproject.toml app
```

### Formating

```shell
black --config ./config/pyproject.toml app
```

Also see the [actions tab](https://github.com/jsolly/awesome-django-blog/actions)
to see if everything is passing.

### Pre-commit Hooks

If there are any Ruff failures (badly linted code), the build will fail, so please make sure you have the pre-commit hook installed.

```
$ cd awesome-django-blog/config
$ pre-commit install
```

### Local server (For mobile testing)

[Use Ngrok](https://ngrok.com/)

---

## Features

### Functional Features

- User profile with avatar (automatic sizing and compression using Pillow)
- User Login with Django built-in auth to create posts and leave comments
- Ckeditor 5 for authoring blog posts (also includes spell check, code snippets, character
  counter, and more!)
- Add real-time comments without page reloads for a smooth user experience.
- Slugified URLs for more readable links
- Open Graph protocol compliant social media sharing for beautiful share cards (LinkedIn, Twitter, Facebook, Instagram, Reddit, etc)
- Smart and powerful Global search so you can find any blog post with a keyword search.
- Display site visitors in a web map
- Portfolio page with testimonials, contact me, Web vitals, and more!
- Light and Dark Theme that automatically switch based on user's current system theme.
- Blog reading time so viewers can estimate how long it will take them to read a post.
- Atom and RSS feed so users can subscribe to your latest blog posts.
- GPT3 powered blog post title, slug, and metadesc generator so you can harness the power of AI in your blog post authoring workflow
- Copy to clipboard anchor links on every header within a blog post so you can share specific sections of a post.
- Site-wide 'breadcumbs' so your users can know exactly where they are and navigate with ease.
- Each page is optimized for viewing (and printing) so break out those 8 1/2 by 11s and print out some content!
- GPT-powered Chatbot that can answer questions about your blog and help you find content.

### Non-Functional Features

- No CSS/Layout frameworks (Bootstrap, Tailwind, etc). All CSS and components are custom and optimized for performance.
- HTMX for dynamic page updates without a page refresh
- Robots.txt, security.txt, and sitemap.xml for optimized SEO and security
- Git hooks for automatic static file generation (manage.py collectstatic)
- GitActions CI integration with coverage, linting, and testing. Push with confidence!
- Compatible with Sqllite or postgres databases for fast protyping and production
- Optimized for Performance, SEO, and A11Y
- Latest Django 4.x
- 95% or above unit code coverage for a maintainable codebase
- 100% linted with [ruff](https://pypi.org/project/ruff/) and PEP8 compliant for beautiful Python code.
- Static scans with [CodeQL](https://codeql.github.com/) and pip
  dependency checks with [Dependabot](https://github.com/dependabot) for automated security and updates.
- Formatted with [Black](https://pypi.org/project/black/) for beauty and readability
- Strict Content Security Policy preventing inline styles and scripts for better security
- Subresource Integrity for better security
- [A+ Score on Mozilla Observatory](<[url](https://observatory.mozilla.org/analyze/blogthedata.com)>)
- 100/100 for Performance, SEO, and Accessibility according to Google Lighthouse
- Automatic Conversion of images (.png, .jpeg, etc) to .webp for blazingly fast image loads.
- Badges for test coverage, passing builds, formatter, and linting
- Automated, rotating backups of blog posts using local and cloud storage
- Status page for monitoring uptime and performance of your blog at https://blogthedata.com/status using Apache Echarts.

## Depreciated Features

- ~~Leaflet.js and OpenLayers maps 🗺~~ (Removed in https://github.com/jsolly/awesome-django-blog/pull/246)
- ~~Honeypot Admin page to automatically block IPs trying to login with an admin account~~ (Removed in
  https://github.com/jsolly/awesome-django-blog/pull/105)
- ~~Ko-Fi donation button ☕️~~ (removed in https://github.com/jsolly/awesome-django-blog/commit/c857bb7599836c614aff523756bbf1381e0dd948)
- ~~Post views and likes~~ (Removed in
  https://github.com/jsolly/awesome-django-blog/pull/77)
- ~~Newsletter Sign up 🗞~~ (removed in https://github.com/jsolly/awesome-django-blog/pull/140)
- ~~Github Integration to show active issue backlog without leaving blog~~ (removed
  in https://github.com/jsolly/awesome-django-blog/pull/121)
  [commit:5c050a5b68d9c8ce7dcf90fdef44377cc28eab6b](https://github.com/jsolly/awesome-django-blog/commit/5c050a5b68d9c8ce7dcf90fdef44377cc28eab6b))
- ~~Custom 404 page that looks really cool. So even if your users are lost, they are still having a good time.~~ Removed in (https://github.com/jsolly/awesome-django-blog/commit/19b3d40cc6e8b231010b0f62656eb27e0104ffd7)

## Contributing

We ♥️ our contributors.

📕 We expect everyone participating in the community to abide by our [Code of Conduct](https://github.com/jsolly/awesome-django-blog/blob/master/docs/CODE_OF_CONDUCT.md). Please read and follow it. <br>
🤝 If you'd like to contribute, start by reading our [Contribution Guide](https://github.com/jsolly/awesome-django-blog/blob/master/docs/CONTRIBUTING.md).<br>
👾 Explore some [good first issues](https://github.com/jsolly/awesome-django-blog/labels/good_first_issue).<br>

Let's build great software together.

### Top Contributors

|                                               John Solly                                               |                                                     Praise Dike                                                      |
| :----------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------: |
|   [![jsolly](https://avatars1.githubusercontent.com/u/9572232?v=3&s=200)](https://github.com/jsolly)   |  [![freedompraise](https://avatars1.githubusercontent.com/u/70984186?v=4&s=200)](https://github.com/freedompraise)   |
| <a href="https://github.com/jsolly" rel="noopener noreferrer" target="_blank"> `github.com/jsolly`</a> | <a href="https://github.com/freedompraise" rel="noopener noreferrer" target="_blank"> `github.com/freedompraise`</a> |

---

## Support

Reach out to me on X!
  <a href="https://twitter.com/_jsolly" rel="noopener noreferrer" target="_blank">
  `@_jsolly`</a>

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
