from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from .utils import answer_question
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
)
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import connection
from django.db.models import Q
import html
import os
import openai
import logging
from datetime import datetime
from django.views.generic import TemplateView
from django.conf import settings
import psycopg
import psutil
import shutil
from users.models import User
from users.utils import handle_no_permission

openai.api_key = os.environ.get("OPENAI_API_KEY")
ez_logger = logging.getLogger("ezra_logger")


class DatabaseStatus:  # pragma: no cover
    def get_status(self):
        postgres_conn = psycopg.connect(
            host=settings.DATABASES["default"]["HOST"],
            port=settings.DATABASES["default"]["PORT"],
            dbname=settings.DATABASES["default"]["NAME"],
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
        )
        with postgres_conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM pg_stat_activity;")
            postgres_active_connections = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'idle in transaction';"
            )
            postgres_slow_queries = cursor.fetchone()[0]
            cursor.execute(
                "SELECT pg_database_size('{}') / 1024 / 1024;".format(
                    settings.DATABASES["default"]["NAME"]
                )
            )
            postgres_disk_space_used = cursor.fetchone()[0]

        return (
            postgres_active_connections,
            postgres_slow_queries,
            postgres_disk_space_used,
        )


class StatusView(TemplateView):
    template_name = "blog/status_page.html"

    def get_context_data(self, **kwargs):
        # Get the status of your Django blog
        blog_status = "up"
        blog_message = "Blog is up and running"
        blog_updated_at = datetime.utcnow().strftime("%B %d, %Y %I:%M %p")
        # You can replace the above values with your own logic to determine the status of your blog

        # Get the status of Postgres
        database_status = DatabaseStatus()
        (
            postgres_active_connections,
            postgres_slow_queries,
            postgres_disk_space_used,
        ) = database_status.get_status()

        # Calculate server uptime
        boot_time = psutil.boot_time()
        uptime_seconds = (
            datetime.now() - datetime.fromtimestamp(boot_time)
        ).total_seconds()
        uptime_days, remainder = divmod(uptime_seconds, 86400)
        uptime_hours, remainder = divmod(remainder, 3600)
        uptime_minutes, _ = divmod(remainder, 60)
        server_uptime = f"{int(uptime_days)} days, {int(uptime_hours)} hours, {int(uptime_minutes)} minutes"

        # Calculate CPU usage
        cpu_usage_percent = psutil.cpu_percent()

        # Calculate RAM usage
        virtual_memory = psutil.virtual_memory()
        ram_used = int(virtual_memory.used / (1024**2))
        ram_total = int(virtual_memory.total / (1024**2))
        ram_percentage = round(virtual_memory.percent)

        # Get the disk usage
        disk_usage_info = shutil.disk_usage("/")
        total, used, free = disk_usage_info
        disk_usage = f"{used // (2 ** 30)}GB / {total // (2 ** 30)}GB"

        context = {
            "title": "Status | Blogthedata.com",
            "description": "Track the uptime and performance of blogthedata.com in real-time. Stay informed of any issues that may affect your browsing experience.",
            "status": blog_status,
            "message": blog_message,
            "updated_at": blog_updated_at,
            "postgres_active_connections": postgres_active_connections,
            "postgres_slow_queries": postgres_slow_queries,
            "postgres_disk_space_used": postgres_disk_space_used,
            "server_uptime": server_uptime,
            "cpu_usage_percent": cpu_usage_percent,
            "ram_used": ram_used,
            "ram_total": ram_total,
            "ram_percentage": ram_percentage,
            "disk_usage": disk_usage,
        }

        return context


class AllPostsView(ListView):
    model = Post
    template_name = "blog/all_posts.html"
    context_object_name = "posts"  # The default is object_list
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.active()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["url"] = self.request.path
        context["title"] = "All Posts | Blogthedata.com"
        context["description"] = "All posts on blogthedata.com"
        return context


class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 3

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Post.objects.all()
        return Post.objects.active()

    def get_template_names(self):
        if self.request.htmx:
            return "blog/parts/posts.html"
        return "blog/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["url"] = self.request.path
        context["title"] = "Solly's Blog | Blogthedata.com"
        context[
            "description"
        ] = "Gain productivity and stay informed on the latest geospatial web dev techniques with blog posts from a geospatial software engineer. Get valuable insights."
        return context


class CategoryView(ListView):
    model = Post
    template_name = "blog/categories.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 3

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs.get("slug"))
        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()
        return posts.filter(category=category.id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        category = get_object_or_404(Category, slug=self.kwargs.get("slug"))
        context["category"] = category
        context["url"] = self.request.path
        context["title"] = f"{category.name.title()} | Blogthedata.com"
        context[
            "description"
        ] = f"Get tips and insights on {category.name.title()} from a geospatial engineer. Read the latest blog posts and stay up-to-date on the latest industry trends."
        return context

    def get_template_names(self):
        if self.request.htmx:
            return "blog/parts/posts.html"
        return "blog/categories.html"


class PortfolioView(ListView):
    model = Post
    template_name = "blog/portfolio.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.active().filter(category__slug="portfolio")

    def get_context_data(self, *args, **kwargs):
        carousel_items = [
            {
                "avatar_url": "portfolio/AmyBrazil.webp",
                "name": "Amy Brazil",
                "position": "Direct Manager",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "I had the pleasure to hire, onboard and manage John...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            {
                "avatar_url": "portfolio/CraigUtley.webp",
                "name": "Craig Utley",
                "position": "Direct Manager",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "There is a right way to come into an organization and John did it the right way...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            {
                "avatar_url": "portfolio/MeredithBean.webp",
                "name": "Meredith Bean",
                "position": "Undergraduate Student",
                "company": "GMU",
                "year": "2016",
                "quote": "John was an extraordinary TA to me as a student in an introductory GIS class...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            {
                "avatar_url": "portfolio/KathrynThorpe.webp",
                "name": "Kathryn Thorpe",
                "position": "Coworker",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "Not only is John the kind of guy you'd trust with all things IT based on his technical prowess...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
        ]
        context = super().get_context_data(*args, **kwargs)
        context["url"] = self.request.path
        context["carousel_items"] = carousel_items
        context["title"] = "Solly's Portfolio | Blogthedata.com"
        context[
            "description"
        ] = "John Solly's portfolio. A geospatial software engineer with a passion for creating beautiful and fast mapping applications."
        return context


class SearchView(ListView):
    model = Post
    template_name = "blog/search_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        searched = self.request.GET.get("searched")
        if not searched:
            return Post.objects.none()

        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()

        if connection.vendor == "postgresql":  # pragma: no cover
            # Use Postgres full-text search
            search_vector = SearchVector("title", weight="A") + SearchVector(
                "content", weight="D"
            )
            search_query = SearchQuery(searched)
            return (
                posts.annotate(
                    search=search_vector, rank=SearchRank(search_vector, search_query)
                )
                .filter(search=search_query)
                .order_by("-rank")
            )
        else:
            # For other DBs (like SQLite), use simple case-insensitive search
            return posts.filter(
                Q(title__icontains=searched) | Q(content__icontains=searched)
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["searched"] = self.request.GET.get("searched")
        context["num_results"] = self.get_queryset().count()
        context["title"] = f"Search Results for {self.request.GET.get('searched')}"
        context[
            "description"
        ] = f"Search results for {self.request.GET.get('searched')}"
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])
        if post.draft:
            get_object_or_404(User, username=self.request.user)

        return Post.objects.filter(slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        context["description"] = self.object.metadesc
        context["comment_form"] = CommentForm()
        return context


class CreatePostView(UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post/add_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create a New Post"
        return context


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post/edit_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        post = self.get_object()
        context["post"] = post
        context["title"] = f"Edit {post.title}"
        context["description"] = f"Edit {post.title}"
        return context


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("home")

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment/add_comment.html"

    def form_valid(self, form):
        form.instance.post = Post.objects.get(slug=self.kwargs["slug"])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def handle_no_permission(self):
        return handle_no_permission(self.request, slug=self.kwargs["slug"])


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment/update_comment.html"
    context_object_name = "comment"

    def get_success_url(self):
        return reverse_lazy("post-detail", kwargs={"slug": self.object.post.slug})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self):
        comment_id = self.kwargs.get("comment_id")
        comment = get_object_or_404(Comment, id=comment_id)
        return comment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = self.get_object()
        context["post"] = comment.post
        context["title"] = f"Edit Comment #{comment.id}"
        context["description"] = f"Edit Comment #{comment.id}"
        return context


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.author == request.user:
            comment.delete()
        return redirect("post-detail", slug=comment.post.slug)


def generate_gpt_input_value(request, post_id):
    blog_post = get_object_or_404(Post, id=post_id)
    prompt_dict = {
        "generate-title": {
            "prompt": f"No pretext or explanations. Write a concise website title for the following blog post: {blog_post.content}",
            "max_tokens": 17,  # ~70 characters
        },
        "generate-slug": {
            "prompt": f"No pretext or explanations. Write a concise website slug based off this blog post title: {request.POST.get('gpt_input', '')}",
            "max_tokens": 17,  # ~70 characters
        },
        "generate-metadesc": {
            "prompt": f"No pretext or explanations. Write a concise website metadesc for the following blog post: {blog_post.content}",
            "max_tokens": 40,  # ~160 characters
        },
    }

    def get_safe_completion(prompt, max_tokens):
        completion = (
            openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.5,
            )["choices"][0]["text"]
            .replace("\n", "")
            .replace('"', "")
        )
        return html.escape(completion)

    def generate_input_field(prompt, max_tokens):
        completion = get_safe_completion(prompt, max_tokens)
        safe_completion = html.escape(completion)
        return f"<input autofocus='' id='id_gpt_input' maxlength='250' name='gpt_input' required_type='text' value='{safe_completion}'>"

    trigger = request.htmx.trigger

    prompt = prompt_dict[trigger]["prompt"]
    max_tokens = prompt_dict[trigger]["max_tokens"]
    new_content = generate_input_field(prompt, max_tokens)
    return HttpResponse(new_content)


@csrf_exempt
def answer_question_with_GPT(request):
    question = request.POST.get("question-text-area", "")
    ez_logger.info(f"Question: {question}")
    completion = answer_question(question=question)
    response = f"<div class='messages__item messages__item--bot'>{completion}</div>"

    return HttpResponse(response)
