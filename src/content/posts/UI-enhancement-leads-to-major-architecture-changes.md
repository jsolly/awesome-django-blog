---
slug: UI-enhancement-leads-to-major-architecture-changes
title: "Django Context Processors and Multi-Stage Migrations: Lessons Learned"
category: web-dev
description: Sometimes minor features need large technical lifts. How a small UI change pushed me to learn Django’s Context Processors and DB Migrations.
draft: false
image: https://d1d7p8ufhgz4ld.cloudfront.net/media/post_metaimgs/context_processor.png
legacyImage: post_metaimgs/context_processor.png
imageAlt: Screenshot of Context Processor Code
imageAttribution: ""
imageWidth: 1280
imageHeight: 688
published: "2022-06-01T18:20:08Z"
updated: "2024-12-23T23:19:07.658Z"
author: John Solly
feedAuthor: John_Solly
legacyAuthorId: 2
excerpt: <p>Sometimes minor features need large technical lifts. How a small UI change pushed me to learn Django’s Context Processors and DB Migrations.</p>
legacyId: 58
related:
  - 15-minute-dump-and-go-instant-pot-recipes
  - cosine-similarity-better-than-tags
  - Adding-views-likes-to-posts
---

Who would have thought the number of posts per category as a badge icon could be tricky? This small UI change taught me about Django's context processors and multi-stage database migrations.

<figure class="image"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image_h9OEyTH.png" alt="Sidebar content showing Site Updates and Life Advice"></figure>

It all started when I found an example on the Bootstrap Docs showing <a target="_blank" rel="noopener noreferrer" href="https://getbootstrap.com/docs/4.0/components/list-group/#with-badges">count badges on list items</a>. I imagined injecting the category count into a template.

<pre><code class="language-html"># templates/sidebar.html
{ category.posts_count }}</code></pre>

Only, I needed the post\_count for every category returned in a QuerySet. I found a promising function in the Django QuerySet doc called <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/models/querysets/#annotate">annotate()</a>

<blockquote><p>Annotates each object in the <strong>QuerySet</strong> with the provided list of <a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/models/expressions/">query expressions</a>. An expression may be a simple value, a reference to a field on the model (or any related models), or an aggregate expression (averages, sums, etc.) that has been computed over the objects that are related to the objects in the <strong>QuerySet</strong>.</p><p><a target="_blank" rel="noopener noreferrer" href="https://docs.djangoproject.com/en/4.0/ref/models/querysets/#annotate">Official Django Doc</a></p></blockquote>

The key here is <i>related</i> models. For annotate( ) to work with multiple models, they need to be related. The only problem with my data model was that Post and Category didn’t know each other! Here is how my Post model looked. The category field is a CharField with no foreign/primary key relationship with the Category class.

<pre><code class="language-python"># models.py
class Post(models.Model):
    title = models.CharField(max_length=60)
    category = models.CharField(max_length=100, default="uncategorized")
    content = CKEditor5Field(blank=True, null=True, config_name='extends')</code></pre>

In my CategoryView, I filtered posts by performing a string match between the Post's category and the Category name by saying something like, "Give me all the Posts that have a category matching the string of the category's name pulled from the URL.

<pre><code class="language-python"># models.py
class CategoryView(ListView):
    model = Post
    def get_queryset(self):
        cat = self.kwargs.get("cat").replace("-", " ")
        posts = Post.objects.all()
        return posts.filter(category=cat)</code></pre>

When a User navigated to <code>/category/site-updates/</code>, the code would take 'site-updates,' remove the hyphen and query the Post table.

<pre><code class="language-sql">SELECT *
FROM Post
WHERE category = "site updates"</code></pre>

Here is how you change a column from CharField to ForeignKey. 

<ol><li>Create the new field and populate all the cells with null values</li><li>Use the RunPython function to copy data into it.</li><li>Delete the old field and re-name the new one to the name of the old one.</li></ol>

I accomplished this with three migrations.

Post table BEFORE migration

<figure class="table"><table><thead><tr><th>post_id</th><th>category</th></tr></thead><tbody><tr><td>0</td><td>site updates</td></tr><tr><td>1</td><td>life advice</td></tr><tr><td>2</td><td>life advice</td></tr></tbody></table></figure>

Category Table

<figure class="table"><table><thead><tr><th>category_id</th><th>name</th></tr></thead><tbody><tr><td>0</td><td>life advice</td></tr><tr><td>1</td><td>site updates</td></tr></tbody></table></figure>

<p style="margin-left:0px;">I first added a column to models.Post called category_link. This is the empty field I’ll use to copy category ids into.&nbsp;</p>

<pre><code class="language-python"># models.py
class Post(models.Model):
    title = models.CharField(max_length=60)
    category = models.CharField(max_length=100, default="uncategorized")
    category_link = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    content = CKEditor5Field(blank=True, null=True, config_name='extends')</code></pre>

After adding category\_link, I run.

<pre><code class="language-bash">$ python3 manage.py makemigrations --name add_temp_category_link_field blog</code></pre>

This generates a new migration file that will add the new field to the Post table to create a relationship with the Category table.

<pre><code class="language-python"># migrations/0017_add_temp_category_link_field.py

from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0016_add_alt_txt_to_meta_img'),
    ]
    operations = [
        migrations.AddField(
            model_name='post',
            name='category_link',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.category'),
        ),
    ]
</code></pre>

<pre><code class="language-bash">$ python manage.py migrate</code></pre>

<figure class="table"><table><thead><tr><th>Post</th><th>Category</th><th>category_link</th></tr></thead><tbody><tr><td>0</td><td>site updates</td><td>&nbsp;</td></tr><tr><td>1</td><td>life advice</td><td>&nbsp;</td></tr><tr><td>2</td><td>life advice</td><td>&nbsp;</td></tr></tbody></table></figure>

The second and third migrations are more hands-on. You need to create empty migrations and then modify them to perform additional actions.

<pre><code class="language-bash">$ python3 manage.py makemigrations --empty --name transfer_categories blog</code></pre>

<pre><code class="language-python"># migrations/0018_transfer_categories.py
from django.db import migrations
class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0017_add_temp_category_link_field"),
    ]
    operations = [
    
    ]</code></pre>

The magic happens in <code>migrations.RunPython</code> which runs Python as part of the migration. I transfer data from the category column to the newly created category\_link field.

<pre><code class="language-python"># migrations/0018_transfer_categories.py
from django.db import migrations
def link_categories(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Category = apps.get_model('blog', 'Category')
    for post in Post.objects.all():
        category, created = Category.objects.get_or_create(name=post.category)
        post.category_link = category
        post.save()
class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0017_add_temp_category_link_field"),
    ]
    operations = [
        migrations.RunPython(link_categories)
    ]</code></pre>

I perform string matching again, but it's allowing me to copy the category ids into my Post table instead of the category name.

<pre><code class="language-bash">$ Python3 manage.py migrate</code></pre>

<figure class="table"><table><thead><tr><th>Post</th><th>Category</th><th>category_link</th></tr></thead><tbody><tr><td>0</td><td>site updates</td><td>1</td></tr><tr><td>1</td><td>life advice</td><td>0</td></tr><tr><td>2</td><td>life advice</td><td>0</td></tr></tbody></table></figure>

I could stop here, but Django is touted as the web framework for <a target="_blank" rel="noopener noreferrer" href="https://www.djangoproject.com">perfectionists with deadlines</a>; I am one of them!

Another empty migration.

<pre><code class="language-bash">$ python3 manage.py migrate --empty --name remove_category_rename_category_link blog</code></pre>

I modify to include logic that removes the old category field and then rename category\_link to category.

<pre><code class="language-python"># migrations/0019_remove_category_rename_category_link.py
from django.db import migrations
class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0018_transfer_categories"),
    ]
    operations = [
        migrations.RemoveField(
            model_name="post",
            name="category",
        ),
        migrations.RenameField(
            model_name="post",
            old_name="category_link",
            new_name="category",
        ),
    ]</code></pre>

<pre><code class="language-bash">$ Python3 manage.py migrate</code></pre>

<figure class="table"><table><thead><tr><th>Post</th><th>Category</th></tr></thead><tbody><tr><td>0</td><td>1</td></tr><tr><td>1</td><td>0</td></tr><tr><td>2</td><td>0</td></tr></tbody></table></figure>

Looks good to me!

Now it's on to the context processor that leverages all this hard work at the database level.

<pre><code class="language-python"># blog/custom_context_processor.py
from .models import Category
from django.db.models import Count


def category_renderer(request):
    cat_list = Category.objects.annotate(posts_count=Count('post'))
    return {
        "cat_list": cat_list,
    }</code></pre>

The magic is all happening on <strong> line 7. </strong> For every category object, I add a Count( ) of posts. Getting the category post count in a template is as easy as <code>{{ category.posts_count }}</code>

The last step is adding a context processor to settings.py, so Django knows to add it to the context in all templates.

<pre><code class="language-python"># settings.py
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                'blog.custom_context_processor.category_renderer'
            ]
        }
    }
]</code></pre>

I removed duplicate category code from my views because the context processor is now adding categories (and their post count) to every template’s context.

The last piece is creating the template code.

<pre><code class="language-html"># templates/sidebar.html
&lt;h3&gt;Navigate to a Category&lt;/h3&gt;
{% for cat_item in cat_list %}
&lt;a href="{% url 'blog-category' cat_item|slugify %}"
  class="list-group-item list-group-item-action {% if request.resolver_match.kwargs.cat == cat_item|slugify %}active{% endif %}"
  id="sidebar-{{ cat_item|slugify }}"&gt;{{cat_item|title}}
  &lt;span class="badge rounded-pill bg-danger float-end"&gt;{{ cat_item.posts_count }}&lt;/span&gt;
&lt;/a&gt;
{% endfor %}</code></pre>

The end result is count badges in the sidebar.

<figure class="image image-style-align-center"><img src="https://d1d7p8ufhgz4ld.cloudfront.net/media/post_imgs/image.png" alt="Sidebar showing badges with post count."></figure>

Crazy how what might seem trivial is actually a major technical undertaking.
