---
slug: how-to-test-and-debug-django-templates
title: Uncover Hidden Errors in Django Templates With django-fastdev
category: dev-tools
description: Uncover hidden errors in Django templates with django-fastdev and coverage plugin. Learn how to write view tests, and get 100% code coverage for your templates.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/django.jpg
legacyImage: post_metaimgs/django.jpg
imageAlt: Protagonist from Django Unchained holding a revolver
imageAttribution: https://www.flickr.com/photos/ilfattoquotidiano/8390397908
imageWidth: 1400
imageHeight: 984
published: "2022-05-14T04:13:09Z"
updated: "2022-05-14T04:13:09Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Uncover hidden errors in Django templates with django-fastdev and coverage plugin. Learn how to write view tests, and get 100% code coverage for your templates.</p>
legacyId: 45
related:
  - implement-continuous-integration-github-actions
  - how-to-get-100-percent-unit-test-coverage
  - two-weird-reasons-I-love-unit-tests
---

By default, Django hides errors like non-existent template variables in templates. One way to un-hide them is to install the <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/django-fastdev/">django-fastdev</a> module.

After installing fastdev, you'll run into errors on startup. Try firing up runserver now that new fatal errors can interrupt app startup.

Next, you'll want to install the <a target="_blank" rel="noopener noreferrer" href="https://coverage.readthedocs.io">coverage python plugin</a>. This allows you to assess test coverage across any Python project. The coverage plugin will assess coverage for most statements, but it doesn't know how to check Django templates. For that, you'll need to get an additional module,  <a target="_blank" rel="noopener noreferrer" href="https://pypi.org/project/django-coverage-plugin/">django-coverage-plugin</a>. To get it working in VScode, I needed to add an environment variable to my .zshrc file. This tells the plugin where your django settings.py file is located.

<pre><code class="language-bash">export DJANGO_SETTINGS_MODULE=django_project.settings</code></pre>

The coverage module works hand-in-hand with unittest (probably pytest and nose too). These are the three most useful CLI commands I run. Check <a target="_blank" rel="noopener noreferrer" href="https://coverage.readthedocs.io/en/6.3.3/">the docs</a> for more info.

<pre><code class="language-bash">coverage run -m unittest discover
coverage report -m --omit 'tests/*' --skip-empty --skip-covered
coverage html --skip-empty --omit tests/tests_isolated -d blog/templates/htmlcov</code></pre>

The first command runs unittest and logs results to a .coverage file used to generate subsequent reports.

The second command generates a report right in the terminal with code coverage. I've added additional parameters.

<ul><li>omit 'tests/* ...I don't need coverage for my test files. I guess that begs a philosophical question...should unit tests be unit tested? Oh boy...</li><li>skip-empty ...Skips any file that has nothing in it. Otherwise, there will be __init__.py files in the report. Gross.</li><li>skip-covered ...It feels good to have 100% coverage, but it's not very useful. This removes files from the report if they already have 100% code coverage.</li></ul>

The final command, coverage html, generates an html report to send to your colleagues!

## Code Coverage for templates

Now that we have a handle on where coverage is lacking, we'll want to test those templates! We don't test templates directly. We test them along with our views. In order to get coverage,  write your view tests so that each statement in a template evaluates.

My test\_views.py file, contains a function called <code>test_category_view( )</code>. At first, I was missing coverage in my templates because it wasn't evaluating all the pagination logic. To get more coverage, I needed to make sure there were enough posts to fill several pages besides fetching those pages in order to make sure I hit all the pagination logic contained in my template.

<pre><code class="language-python"># Paginated list appears when there are many posts
create_several_posts(self.category1.name, self.super_user, 20)
response = self.client.get(self.category_url)
self.assertTrue(response.context['is_paginated'])
self.assertEqual(response.context['posts'].count(), 5) # 5 per page

# Paginated list works when user has moved forward at least one page
response = self.client.get(self.category_url, {'page': 2})
self.assertTrue(response.context['page_obj'].has_previous())</code></pre>

The <code>create_several_posts</code> function ensures 20 posts are created before the test continues. You'll have to keep playing with your test\_views file to get more and more template coverage. Eventually, coverage will look like this:

<pre><code class="language-python">Name                                                                Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------
django_project/blog/admin.py                                           11      0   100%
django_project/blog/apps.py                                             3      0   100%
django_project/blog/forms.py                                           13      0   100%
django_project/blog/models.py                                          64      0   100%
django_project/blog/templates/blog/add_comment.html                    12      0   100%
django_project/blog/templates/blog/add_post.html                       16      0   100%
django_project/blog/templates/blog/categories.html                      8      0   100%
django_project/blog/templates/blog/edit_post.html                      12      0   100%
django_project/blog/templates/blog/home.html                           14      0   100%
django_project/blog/templates/blog/parts/about_me.html                 28      0   100%
django_project/blog/templates/blog/parts/base.html                     70      0   100%
django_project/blog/templates/blog/parts/footer.html                   18      0   100%
django_project/blog/templates/blog/parts/header.html                   61      0   100%
django_project/blog/templates/blog/parts/kofi_donation.html             1      0   100%
django_project/blog/templates/blog/parts/mailchimp_embed.html          37      0   100%
django_project/blog/templates/blog/parts/pagination.html               20      0   100%
django_project/blog/templates/blog/parts/posts.html                    16      0   100%
django_project/blog/templates/blog/parts/sidebar.html                  13      0   100%
django_project/blog/templates/blog/pgp-key.txt                         98      0   100%
django_project/blog/templates/blog/post_confirm_delete.html            15      0   100%
django_project/blog/templates/blog/post_detail.html                    63      0   100%
django_project/blog/templates/blog/roadmap.html                        34      0   100%
django_project/blog/templates/blog/search_posts.html                   15      0   100%
django_project/blog/templates/blog/security.txt                         5      0   100%
django_project/blog/templates/blog/user_posts.html                      3      0   100%
django_project/blog/templates/blog/works_cited.html                    11      0   100%
django_project/blog/urls.py                                             7      0   100%
django_project/blog/utils.py                                           19      0   100%
django_project/blog/views.py                                          171      0   100%
django_project/django_project/settings.py                              65      0   100%
django_project/django_project/sitemaps.py                              17      0   100%
django_project/django_project/urls.py                                  12      0   100%
django_project/users/admin.py                                           3      0   100%
django_project/users/apps.py                                            5      0   100%
django_project/users/forms.py                                          23      0   100%
django_project/users/models.py                                         18      0   100%
django_project/users/signals.py                                        11      0   100%
django_project/users/templates/users/login.html                        22      0   100%
django_project/users/templates/users/logout.html                        7      0   100%
django_project/users/templates/users/password_reset.html               13      0   100%
django_project/users/templates/users/password_reset_complete.html       5      0   100%
django_project/users/templates/users/password_reset_done.html           4      0   100%
django_project/users/templates/users/profile.html                      21      0   100%
django_project/users/templates/users/register.html                     20      0   100%
django_project/users/views.py                                          67      0   100%
-------------------------------------------------------------------------------------------------
TOTAL                                                                1171      0   100%</code></pre>

Good luck testing your templates!
