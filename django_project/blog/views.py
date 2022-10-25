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


class HomeView(ListView):
    model = Post
    template_name = "blog/home.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 10

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
        return context


class CategoryView(ListView):
    model = Post
    template_name = "blog/post/categories.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 10

    def get_queryset(self):
        category = self.kwargs.get("category").replace("-", " ")
        category = get_object_or_404(Category, name=category)
        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()
        return posts.filter(category=category.id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["category"] = Category.objects.get(
            name=self.kwargs["category"].replace("-", " ")
        )
        context["url"] = self.request.path
        return context

    def get_template_names(self):
        if self.request.htmx:
            return "blog/parts/posts.html"
        return "blog/post/categories.html"


@csrf_exempt
def search_view(request):
    """Controls what is shown to a user when they search for a post."""
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
            "blog/post/search_posts.html",
            {"searched": searched, "posts": filtered_posts},
        )
    return render(
        request,
        "blog/post/search_posts.html",
        {"searched": "", "posts": []},
    )
    # Seems to be the best approach for now
    # https://stackoverflow.com/questions/53146842/check-if-text-exists-in-django-template-context-variable


class PostDetailView(DetailView):
    """
    Controls everything to do with what a user sees when viewing a single post.
    """

    model = Post
    template_name = "blog/post/post_detail.html"

    def get_queryset(self):
        post = get_object_or_404(Post, slug=self.kwargs["slug"])
        if post.draft:
            get_object_or_404(User, username=self.request.user)

        return Post.objects.filter(slug=self.kwargs["slug"])


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


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("home")

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
