from .models import Post, Category
from .forms import PostForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
import aiohttp
import asyncio
import ssl


class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Post.objects.all()
        return Post.objects.active()


class UserPostListView(ListView):  # Not actively worked on
    model = Post
    template_name = "blog/user_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


class PostDetailView(DetailView):
    """
    Controls everything to do with what a user sees when viewing a single post.
    """

    model = Post
    template_name = "blog/post_detail.html"

    def get_queryset(self):
        post = Post.objects.get(slug=self.kwargs["slug"])
        if post.draft:
            get_object_or_404(User, username=self.request.user)

        return Post.objects.filter(slug=self.kwargs["slug"])


class CreatePostView(UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/add_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/edit_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy("blog-home")

    # def test_func(self):
    #     post = self.get_object()
    #     if self.request.user == post.author:
    #         return True


class CategoryView(ListView):
    model = Post
    template_name = "blog/categories.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 5

    def get_queryset(self):
        category = self.kwargs.get("category").replace("-", " ")
        category = Category.objects.get(name=category)
        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()
        return posts.filter(category=category.id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["category"] = Category.objects.get(
            name=self.kwargs["category"].replace("-", " ")
        )
        return context


def road_map_view(request):
    from django_project.settings import GIT_TOKEN
    from datetime import date

    # project_url = "https://api.github.com/projects/14278916"
    in_progress_column_url = "https://api.github.com/projects/columns/18242400"
    backlog_column_url = "https://api.github.com/projects/columns/18271705"
    next_sprint_column_url = "https://api.github.com/projects/columns/18739295"
    HEADERS = {"Authorization": f"token {GIT_TOKEN}"}

    async def make_request(session, url, params=None):
        async with session.get(url, params=params, ssl=ssl.SSLContext()) as resp:
            return await resp.json()

    async def main(urls):
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks = []
            for url in urls:
                tasks.append(asyncio.ensure_future(make_request(session, url)))

            tasks.append(
                asyncio.ensure_future(
                    make_request(
                        session,
                        url="https://api.github.com/repos/jsolly/blogthedata/issues",
                        params={"state": "open"},
                    )
                )
            )

            return await asyncio.gather(*tasks)

    urls = [
        f"{in_progress_column_url}/cards",
        f"{backlog_column_url}/cards",
        f"{next_sprint_column_url}/cards",
    ]

    inprog_cards, backlog_cards, next_sprint_cards, all_open_issues = asyncio.run(
        main(urls)
    )

    inprog_issue_urls = [card["content_url"] for card in inprog_cards]
    backlog_issue_urls = [card["content_url"] for card in backlog_cards]
    next_sprint_issue_urls = [card["content_url"] for card in next_sprint_cards]

    inprog_issues = [
        issue for issue in all_open_issues if issue["url"] in inprog_issue_urls
    ]
    backlog_issues = [
        issue for issue in all_open_issues if issue["url"] in backlog_issue_urls
    ]
    next_sprint_issues = [
        issue for issue in all_open_issues if issue["url"] in next_sprint_issue_urls
    ]

    sprint_number = date.today().isocalendar()[1] // 2  # Two week sprints
    return render(
        request,
        "blog/roadmap.html",
        {
            "all_open_issues": all_open_issues,
            "backlog_issues": backlog_issues,
            "inprog_issues": inprog_issues,
            "next_sprint_issues": next_sprint_issues,
            "sprint_number": sprint_number,
        },
    )


@csrf_exempt
def search_view(request):
    """Controls what is shown to a user when they search for a post. A note...I never bothered to make sure admins could see draft posts in this view"""
    if request.method == "POST":
        searched = request.POST["searched"]
        posts = Post.objects.active()
        if request.user.is_staff or request.user.is_superuser:
            posts = Post.objects.all()
        filtered_posts = posts.filter(
            Q(content__icontains=searched) | Q(title__icontains=searched)
        )
        return render(
            request,
            "blog/search_posts.html",
            {"searched": searched, "posts": filtered_posts},
        )
    return render(
        request,
        "blog/search_posts.html",
        {"searched": "", "posts": []},
    )
    # Seems to be the best approach for now
    # https://stackoverflow.com/questions/53146842/check-if-text-exists-in-django-template-context-variable


def works_cited_view(request):
    return render(
        request,
        "blog/works_cited.html",
    )


def site_analytics_view(request):
    return render(
        request,
        "blog/site_analytics.html",
    )


def security_txt_view(request):
    return render(
        request,
        "blog/security.txt",
    )


def security_pgp_key_view(request):
    return render(
        request,
        "blog/pgp-key.txt",
    )
