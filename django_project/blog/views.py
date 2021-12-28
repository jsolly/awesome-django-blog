from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    UpdateView,
)
from .models import Post, Comment, Category, IpPerson
from django.forms import widgets
from django.urls import reverse
from .forms import PostForm, CommentForm


class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    ordering = ["-date_posted"]
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()
        return context


class UserPostListView(ListView):
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
    model = Post
    template_name = "blog/post_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context["cat_list"] = Category.objects.all()

        like_status = False
        ip = get_client_ip(self.request)
        if self.object.likes.filter(id=IpPerson.objects.get(ip=ip).id).exists():
            like_status = True
        
        context['like_status'] = like_status
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
        form.instance.post = Post.objects.get(id=self.kwargs["pk"])
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
    ordering = ["-date_posted"]
    paginate_by = 5

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryView, self).get_context_data(*args, **kwargs)
        context["category_posts"] = Post.objects.filter(
            category=self.kwargs["cat"].replace("-", " ")
        )
        context["cat_list"] = Category.objects.all()
        context["cat"] = self.kwargs["cat"].replace("-", " ")
        return context


def AboutView(request):
    cat_list = Category.objects.all()
    return render(
        request,
        "blog/about.html",
        {"cat_list": cat_list},
    )


def get_client_ip(request):
    x_forward_for = request.META.get("HTTP_X_FORWARD_FOR")

    if x_forward_for:
        ip = x_forward_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def PostLikeView(request, pk):
    post = Post.objects.get(pk=pk)
    ip = get_client_ip(request)
    if not IpPerson.objects.filter(ip=ip).exists():
        IpPerson.objects.create(ip=ip)
    if post.likes.filter(id=IpPerson.objects.get(ip=ip).id).exists():
        post.likes.remove(IpPerson.objects.get(ip=ip))
    else:
        post.likes.add(IpPerson.objects.get(ip=ip))
    return HttpResponseRedirect(reverse("post-detail", args=[pk]))
