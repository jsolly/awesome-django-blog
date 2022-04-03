from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    UpdateView,
)
from users.models import Profile
import requests
from django_project.settings import GIT_TOKEN
HEAD = {"Authorization": f"token {GIT_TOKEN}"}
from .models import Post, Comment, Category, IpPerson
from .forms import PostForm, CommentForm
from .utils import get_client_ip

class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return Post.objects.all()
        return Post.objects.active()

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class UserPostListView(ListView):  # Not actively worked on
    model = Post
    template_name = "blog/user_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")

    def get_context_data(self, *args, **kwargs):
        context = super(UserPostListView, self).get_context_data(
            *args, **kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class PostDetailView(DetailView):
    """
    Controls everything to do with what a user sees when viewing a single post.
    """
    model = Post
    template_name = "blog/post_detail.html"

    def get_context_data(self, *args, **kwargs):
        """Need to re-generate context based on whether user has viewed post or not"""
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()

        ip = get_client_ip(self.request)
        post = Post.objects.get(slug=self.object.slug)
        # Check to see if we should +1 view count
        if not IpPerson.objects.filter(ip=ip).exists():
            IpPerson.objects.create(ip=ip)

        post.views.add(IpPerson.objects.get(ip=ip))

        # Check to see if we should +1 total likes
        like_status = False
        try:
            if self.object.likes.filter(id=IpPerson.objects.get(ip=ip).id).exists():
                like_status = True
        except IpPerson.DoesNotExist:
            pass

        context["like_status"] = like_status
        return context


class CreatePostView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/add_post.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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
        return False


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/add_comment.html"

    def form_valid(self, form):
        form.instance.post = Post.objects.get(slug=self.kwargs["slug"])
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(DeleteView, LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class CategoryView(ListView):
    model = Post
    template_name = "blog/categories.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "category_posts"  # The default is object_list
    paginate_by = 5

    def get_queryset(self):
        cat = self.kwargs.get("cat").replace("-", " ")
        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()
        return posts.filter(category=cat)

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()
        context["cat"] = self.kwargs["cat"].replace("-", " ")
        return context


def AboutView(request):
    cat_list = Category.objects.all()
    my_profile = Profile.objects.get(id=2)
    return render(
        request,
        "blog/about.html",
        {"cat_list": cat_list, "my_profile": my_profile},
    )


def RoadMapView(request):
    all_issues = requests.request(
        method="GET", url='https://api.github.com/repos/jsolly/blogthedata/issues', params={'state':'open'}, headers=HEAD).json()

    inprog_cards = requests.request(
            method="GET", url='https://api.github.com/projects/columns/18242400/cards', headers=HEAD,
        ).json()
    inprog_issue_urls = [card['content_url'] for card in inprog_cards ]
    backlog_issues = [issue for issue in all_issues if issue['url'] not in inprog_issue_urls]
    inprog_issues = [issue for issue in all_issues if issue['url'] in inprog_issue_urls]

    cat_list = Category.objects.all()
    return render(
        request,
        "blog/roadmap.html",
        {"cat_list": cat_list,
        "backlog_issues": backlog_issues,
        "inprog_issues": inprog_issues,}
    )


def PostLikeView(request, slug):
    post = Post.objects.get(slug=slug)
    ip = get_client_ip(request)
    if not IpPerson.objects.filter(ip=ip).exists():
        IpPerson.objects.create(ip=ip)
    if post.likes.filter(id=IpPerson.objects.get(ip=ip).id).exists():
        post.likes.remove(IpPerson.objects.get(ip=ip))
    else:
        post.likes.add(IpPerson.objects.get(ip=ip))
    return HttpResponseRedirect(reverse("post-detail", args=[str(slug)]))


def SearchView(request):
    """Controls what is shown to a user when they search for a post. A note...I never bothered to make sure admins could see draft posts in this view"""
    cat_list = Category.objects.all()
    if request.method == 'POST':
        searched = request.POST['searched']
        posts = Post.objects.active()
        if request.user.is_staff or request.user.is_superuser:
            posts = Post.objects.all()
        filtered_posts = posts.filter(
            Q(content__icontains=searched) | Q(title__icontains=searched))
        return render(
            request,
            "blog/search_posts.html",
            {"cat_list": cat_list, "searched": searched,
                "filtered_posts": filtered_posts},
        )
    else:
        return render(
            request,
            "blog/search_posts.html",
            {"cat_list": cat_list},
        )

def UnitTestView(request, filename=None):
    cat_list = Category.objects.all()
    html_path = "htmlcov/index.html"
    if filename:
        html_path = f"htmlcov/{filename}"

    return render(
        request,
        html_path,
        {"cat_list": cat_list}
    )