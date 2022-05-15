from .models import Post, Comment, Category, IpPerson
from .forms import PostForm, CommentForm
from .utils import get_client_ip, get_post_like_status
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from users.models import Profile
import requests
from django_project.settings import GIT_TOKEN

HEAD = {"Authorization": f"token {GIT_TOKEN}"}


def add_ip_person_if_not_exist(request):
    ip_adrr = get_client_ip(request)
    # Check to see if we should +1 view count (for this IpPerson)
    try:
        return IpPerson.objects.get(ip=ip_adrr)
    except IpPerson.DoesNotExist:
        return IpPerson.objects.create(ip=ip_adrr)


def add_ip_person_view_if_not_exist(request, post):
    ip_person = add_ip_person_if_not_exist(request)
    ip_adrr = get_client_ip(request)
    if post.views.filter(ip=ip_adrr).exists():
        return ip_person

    post.views.add(ip_person)
    return ip_person


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
        context = super(UserPostListView, self).get_context_data(*args, **kwargs)
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
        context = super().get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()

        post = Post.objects.get(slug=self.object.slug)
        add_ip_person_view_if_not_exist(self.request, post)

        context["like_status"] = get_post_like_status(self.request, post)
        return context


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


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/add_comment.html"

    def form_valid(self, form):
        form.instance.post = Post.objects.get(slug=self.kwargs["slug"])
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy("blog-home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat_list"] = Category.objects.all()
        return context

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
        cat = self.kwargs.get("cat").replace("-", " ")
        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()
        return posts.filter(category=cat)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()
        context["cat"] = Category.objects.get(name=self.kwargs["cat"].replace("-", " "))
        return context


def about_view(request):
    cat_list = Category.objects.all()
    my_user = User.objects.get(username="John_Solly")
    my_profile = Profile.objects.get(user=my_user)
    return render(
        request,
        "blog/about.html",
        {"cat_list": cat_list, "my_profile": my_profile},
    )


def road_map_view(request):
    all_issues = requests.request(
        method="GET",
        url="https://api.github.com/repos/jsolly/blogthedata/issues",
        params={"state": "open"},
        headers=HEAD,
    ).json()

    inprog_cards = requests.request(
        method="GET",
        url="https://api.github.com/projects/columns/18242400/cards",
        headers=HEAD,
    ).json()
    inprog_issue_urls = [card["content_url"] for card in inprog_cards]
    backlog_issues = [
        issue for issue in all_issues if issue["url"] not in inprog_issue_urls
    ]
    inprog_issues = [issue for issue in all_issues if issue["url"] in inprog_issue_urls]

    cat_list = Category.objects.all()
    return render(
        request,
        "blog/roadmap.html",
        {
            "cat_list": cat_list,
            "backlog_issues": backlog_issues,
            "inprog_issues": inprog_issues,
        },
    )


def post_like_view(request, slug):
    post = Post.objects.get(slug=slug)
    ip_adrr = get_client_ip(request)

    ip_person = add_ip_person_view_if_not_exist(request, post)

    if post.likes.filter(id=ip_person.id).exists():
        post.likes.remove(IpPerson.objects.get(ip=ip_adrr))
    else:
        post.likes.add(ip_person)
    return HttpResponseRedirect(reverse("post-detail", args=[str(slug)]))


def search_view(request):
    """Controls what is shown to a user when they search for a post. A note...I never bothered to make sure admins could see draft posts in this view"""
    cat_list = Category.objects.all()
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
            {"cat_list": cat_list, "searched": searched, "posts": filtered_posts},
        )
    return render(
        request,
        "blog/search_posts.html",
        {"cat_list": cat_list, "searched": "", "posts": []},
    )
    # Seems to be the best approach for now
    # https://stackoverflow.com/questions/53146842/check-if-text-exists-in-django-template-context-variable


def works_cited_view(request):
    cat_list = Category.objects.all()
    return render(
        request,
        "blog/works_cited.html",
        {"cat_list": cat_list},
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
