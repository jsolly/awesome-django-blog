from .models import Post, Category
from .forms import PostForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import HttpResponse
from django.utils.text import slugify
import html


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
        return context


class CategoryView(ListView):
    model = Post
    template_name = "blog/post/categories.html"  # <app>/<model>_<viewtype>.html
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
        context["category"] = Category.objects.get(slug=self.kwargs["slug"])
        context["url"] = self.request.path
        return context

    def get_template_names(self):
        if self.request.htmx:
            return "blog/parts/posts.html"
        return "blog/post/categories.html"


class PortfolioView(ListView):
    model = Post
    template_name = "blog/portfolio.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"  # The default is object_list
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.active().filter(category__slug="portfolio")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["url"] = self.request.path
        return context


class SearchView(ListView):
    model = Post
    template_name = "blog/post/search_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        searched = self.request.GET.get("searched")
        posts = Post.objects.active()
        if self.request.user.is_staff or self.request.user.is_superuser:
            posts = Post.objects.all()

        # Create a SearchVector that combines the title and content fields of the Post model
        search_vector = SearchVector("title", weight="A") + SearchVector(
            "content", weight="D"
        )
        # Create a SearchQuery from the user's search input
        search_query = SearchQuery(searched)
        # Return the filtered queryset of Posts, ordered by relevance
        return (
            posts.annotate(
                search=search_vector, rank=SearchRank(search_vector, search_query)
            )
            .filter(search=search_query)
            .order_by("-rank")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["searched"] = self.request.GET.get("searched")
        context["num_results"] = self.get_queryset().count()
        return context


class PostDetailView(DetailView):
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


def count_characters(request):
    trigger = request.htmx.trigger_name
    characters = request.POST[trigger]
    character_count = len(characters)
    return HttpResponse(character_count)


def generate_gpt_input_value(request, post_id):
    import os
    import openai

    def get_safe_completion(prompt, max_tokens):
        completion = (
            openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=max_tokens,  # 1 token is approximately 4 English characters.
                temperature=0.5,
            )["choices"][0]["text"]
            .replace("\n", "")
            .replace('"', "")
        )
        safe_completion = html.escape(completion)
        return safe_completion

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    if request.method == "POST":
        blog_post = get_object_or_404(Post, id=post_id)

        if request.htmx.trigger == "generate-title":
            prompt = f"No pretext or explanations. Write a concise website title for the following blog post: {blog_post.content}"
            completion = get_safe_completion(prompt, max_tokens=17)  # ~70 characters
            new_content = f"<input autofocus='' class='form-control' id='id_gpt_input' maxlength='250' name='gpt_input' required_type='text' value='{completion}'>"
            return HttpResponse(new_content)

        if request.htmx.trigger == "generate-slug":
            prompt = f"No pretext or explanations. Write a concise website slug based off this blog post title: {request.POST['gpt_input']}"
            completion = slugify(
                get_safe_completion(prompt, max_tokens=17)
            )  # ~70 characters
            new_content = f"<input autofocus='' class='form-control' id='id_gpt_input' maxlength='250' name='gpt_input' required_type='text' value='{completion}'>"
            return HttpResponse(new_content)

        if request.htmx.trigger == "generate-metadesc":
            prompt = f"No pretext or explanations. Write a concise website metadesc for the following blog post: {blog_post.content}"
            completion = get_safe_completion(prompt, max_tokens=40)  # ~160 characters.
            new_content = f"<input autofocus='' class='form-control' id='id_gpt_input' maxlength='250' name='gpt_input' required_type='text' value='{completion}'>"
            return HttpResponse(new_content)


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
        return context


class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("home")

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
