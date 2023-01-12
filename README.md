# blogthedata

A blog about Python and JavaScript web development that also includes a portfolio page.

[![Build Status](http://img.shields.io/travis/badges/badgerbadgerbadger.svg?style=flat-square)](https://travis-ci.org/badges/badgerbadgerbadger)
[![Coverage Status](http://img.shields.io/coveralls/badges/badgerbadgerbadger.svg?style=flat-square)](https://coveralls.io/r/badges/badgerbadgerbadger)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

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

### Set up database

- See commented out Database section in
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
- rename 'sample.env' to .env and change the values to match your setup
  (database passwords, secret keys, etc)
  ```shell
  $ python3 manage.py runserver
  ```

---

## Features

#### Functional Features

- User login (header links removed in
  [commit:5c050a5b68d9c8ce7dcf90fdef44377cc28eab6b](https://github.com/jsolly/blogthedata/commit/5c050a5b68d9c8ce7dcf90fdef44377cc28eab6b))
- Create posts filtered by category or author
- Create Comments (Removed in https://github.com/jsolly/blogthedata/pull/77)
- User profile with avatar (automatic sizing and compression using Pillow)
- Ckeditor 5 for rich text (also includes spell check, code snippets, character
  counter, and more!)
- Multiple categoires to organize posts
- Post views and likes (Removed in
  https://github.com/jsolly/blogthedata/pull/77)
- Newsletter Sign up 🗞 (removed in https://github.com/jsolly/blogthedata/pull/140)
- Github Integration to show active issue backlog without leaving blog (removed
  in https://github.com/jsolly/blogthedata/pull/121)
- Slugified URLs
- Open Graph protocol compliant social media sharing
- Global search
- Ko-Fi donation button ☕️ (removed in https://github.com/jsolly/blogthedata/commit/c857bb7599836c614aff523756bbf1381e0dd948)
- Leaflet.js and OpenLayers maps 🗺
- Display site visitors in a web map
- Portfolio page with testimonials, contact me, Web vitals, and more!
- Light and Dark Theme

#### Non-Functional Features

- Robots.txt, security.txt, and sitemap.xml
- Honeypot Admin page (Removed in
  https://github.com/jsolly/blogthedata/pull/105)
- Git hooks for automatic static file generation
- GitActions CI integration with coverage, linting, and testing
- Bootstrap 5
- Compatible with Sqllite or postgres
- Optimized for Performance, SEO, and A11Y
- Latest Django 4.x
- Fully PEP 8 compliant (with some exceptions)
- 95% or above unit code coverage
- 100% linted with [flake8](<[url](https://pypi.org/project/flake8/)>)
- Static scans with [CodeQL](<[url](https://codeql.github.com/)>) and pip
  dependency checks with [Dependabot](<[url](https://github.com/dependabot)>)
- Formatted with [Black](<[url](https://pypi.org/project/black/)>)
- Strict Content Security Policy preventing inline styles and scripts
- Subresource Integrity
- [A+ Score on Mozilla Observatory](<[url](https://observatory.mozilla.org/analyze/blogthedata.com)>)
- Excellent scores on Google Lighthouse
- Custom 404 page
- Automatic Conversion of images (.png, .jpeg, etc) to .webp

## Coverage, Tests, Linting, Hooks

#### Coverage

```shell
$ coverage run -m pytest django_project
$ coverage report -m --skip-covered
```

#### Test

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

#### Lint

```shell
$ flake8 django_project
```

Also see the [actions tab](<[url](https://github.com/jsolly/blogthedata/actions)>)
to see if everything is passing.

#### Pre-commit Hooks (Optional as the CI also takes care of it)
```
$ cd blogthedata
$ chmod +x run_tests.sh
$ pre-commit install
```
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
