# blogthedata

A django blog about data-driven decisions

[![Build Status](http://img.shields.io/travis/badges/badgerbadgerbadger.svg?style=flat-square)](https://travis-ci.org/badges/badgerbadgerbadger) [![Coverage Status](http://img.shields.io/coveralls/badges/badgerbadgerbadger.svg?style=flat-square)](https://coveralls.io/r/badges/badgerbadgerbadger) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

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

- Clone repo https://github.com/jsolly/blogthedata.git
- Install Python and dependencies using requirements stored in config/requirements.txt


### Setup
- See commented out Database section in [django_project/settings.py](https://github.com/jsolly/blogthedata/blob/master/django_project/django_project/settings.py) to use sqllite database or postgres
- python3 manage.py migrate

---

## Features
- User login
- Ability to create posts and comments
- Ckeditor for rich text (also includes spell check, code snippets, character counter, and more!)
- Multiple categoires to organize posts
- Post views and likes
- Newsletter Sign up
- Github Integration
- Optimized for Performance, SEO, and A11Y
- Latest Django 3.x
- Slugified URLs 
- Open Graph protocol compliant social media sharing
- Bootstrap 5
- Compatible with Sqllite or postgres
- Git hooks for automatic static file generation
- Global search
- 100% code coverage
- Fully PEP 8 compliant (with some exceptions*)

## Coverage, Tests, Linting
Contained within tests/
#### Coverage
coverage run -m unittest discover django_project 
coverage report -m --skip-empty --skip-covered
#### Test
unittest discover django_project
#### Lint
flake8 django_project

Also see the [actions tab]([url](https://github.com/jsolly/blogthedata/actions)) to see if everything is passing.

---

## Contributing

Want to work on this with me? DM me [@effortlessgis]([url](https://twitter.com/effortlessgis))

### Step 1

- **Option 1**
    - 🍴 Fork this repo!

- **Option 2**
    - 👯 Clone to your local machine using `https://github.com/jsolly/blogthedata.git`

### Step 2

- **HACK AWAY!** 🔨🔨🔨

### Step 3

- 🔃 Create a new pull request using <a href="https://github.com/jsolly/blogthedata/compare" target="_blank">`https://github.com/jsolly/blogthedata/compare`</a>.

---

## Team

| John Solly |
| :---:
| [![FVCproductions](https://avatars1.githubusercontent.com/u/9572232?v=3&s=200)](https://github.com/jsolly)
| <a href="http://github.com/fvcproductions" target="_blank">`github.com/jsolly`</a> |

---

## FAQ

- **How do I do things?**

    ```bash
    TODO
    ```

---

## Support

Reach out to me at one of the following places!

- Twitter at <a href="https://twitter.com/effortlessgis" target="_blank">`@effortlessgis`</a>

---

## Donations

### Coming Soon

---

## License

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](http://badges.mit-license.org)

- **[MIT license](http://opensource.org/licenses/mit-license.php)**
