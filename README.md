# Awesome Django Blog

[![awesome-django-blog-tests](https://github.com/jsolly/awesome-django-blog/actions/workflows/django-test-deploy-master.yaml/badge.svg)](https://github.com/jsolly/awesome-django-blog/actions/workflows/django-test-deploy-master.yaml)
[![Coverage Status](https://coveralls.io/repos/github/jsolly/awesome-django-blog/badge.svg?branch=master&service=github)](https://coveralls.io/github/jsolly/awesome-django-blog?branch=master)
![CodeStyle](https://img.shields.io/badge/ruff-orange?logo=ruff&label=code-style)
![Linting](https://img.shields.io/badge/ruff-orange?logo=ruff&label=linting)
![PythonVersion](https://img.shields.io/badge/3.11-yellow?logo=Python&logoColor=yellow&label=Python)
[![License](https://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

Awesome-django-blog is a fully functional blogging platform built using the Django web framework. It includes features such as creating and managing blog posts, comments, and categories, as well as user authentication and authorization.

![image](https://github.com/jsolly/awesome-django-blog/assets/9572232/e0066fc2-d68e-4561-b3e4-18ece55e09b2)



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
pip install -r requirements.txt
python3 app/manage.py migrate
python3 manage.py runserver
```

### Seed Posts (Optional)
This command creates sample posts.
```shell
python3 app/manage.py import_posts utilities/seed_posts/posts.json
```


<!-- ## Installation (Docker)

```shell
git clone https://github.com/jsolly/awesome-django-blog.git
cd awesome-django-blog
docker-compose build
docker-compose run --rm app sh -c "python manage.py createsuperuser"
docker-compose up
``` -->

### Default Accounts
The app comes preinstalled with two users. One is an admin and the other can only add comments to posts. 

**(Username/Password)**: 
- admin/admin<br>
- comment_only/comment_only

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
ruff format app
```

Also see the [actions tab](https://github.com/jsolly/awesome-django-blog/actions)
to see if everything is passing.

### Pre-commit Hooks

If there are any Ruff failures (badly linted code), the build will fail, so please make sure you have the pre-commit hook installed.

```
$ cd awesome-django-blog/config
$ pre-commit install
```

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
- Light and Dark Theme that automatically switch based on user's current system theme.
- Blog reading time so viewers can estimate how long it will take them to read a post.
- Atom and RSS feed so users can subscribe to your latest blog posts.
- GPT3 powered blog post title, slug, and metadesc generator so you can harness the power of AI in your blog post authoring workflow
- Copy to clipboard anchor links on every header within a blog post so you can share specific sections of a post.
- Site-wide 'breadcumbs' so your users can know exactly where they are and navigate with ease.
- Each page is optimized for viewing (and printing) so break out those 8 1/2 by 11s and print out some content!
- GPT-powered Chatbot that can answer questions about your blog and help you find content.
- Related posts at the end of each post detail page so users can quickly navigate to a similar post on your blog.
- Syntax highlighting with Prism.js for beautiful code blocks in a variety of languages. Also includes line numbers and copy to clipboard functionality. Automatically changes light/dark theme based on user's current system theme.

### Non-Functional Features

- No CSS/Layout frameworks (Bootstrap, Tailwind, etc). All CSS and components are custom and optimized for performance.
- HTMX for dynamic page updates without a page refresh
- Robots.txt, security.txt, and sitemap.xml for optimized SEO and security
- Git hooks for automatic static file generation (manage.py collectstatic)
- GitActions CI integration with coverage, linting, and testing. Push with confidence!
- Compatible with Sqllite or postgres databases for fast protyping and production
- Optimized for Performance, SEO, and A11Y
- Latest Django 5.x
- 95% or above unit code coverage for a maintainable codebase
- 100% linted with [ruff](https://pypi.org/project/ruff/) and PEP8 compliant for beautiful Python code.
- Static scans with [CodeQL](https://codeql.github.com/) and pip
  dependency checks with [Dependabot](https://github.com/dependabot) for automated security and updates.
- Formatted with [Ruff](https://github.com/astral-sh/ruff) for beauty and speed.
- Strict Content Security Policy preventing inline styles and scripts for better security
- Subresource Integrity for better security
- [A+ Score on Mozilla Observatory](<[url](https://observatory.mozilla.org/analyze/blogthedata.com)>)
- 100/100 for Performance, SEO, and Accessibility according to Google Lighthouse
- Automatic Conversion of images (.png, .jpeg, etc) to .webp for blazingly fast image loads.
- Badges for test coverage, passing builds, formatter, and linting
- Automated, rotating backups of blog posts using local and cloud storage
- Status page for monitoring uptime and performance of your blog at https://blogthedata.com/status using Apache Echarts.
- Custom 404 and 500 pages that look really cool. So even if your users are lost or your app is broke, they are still having a good time.

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
- ~~Portfolio page with testimonials, contact me, Web vitals, and more!~~ (removed in https://github.com/jsolly/awesome-django-blog/pull/404)

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
