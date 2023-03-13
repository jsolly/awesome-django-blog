from .models import Post, Category
from .forms import PostForm
from .utils import answer_question
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
import html
import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")


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
        carousel_items = [
            {
                "avatar_url": "portfolio/AmyBrazil.webp",
                "name": "Amy Brazil",
                "position": "Direct Manager, Customer Success",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "I had the pleasure to hire, onboard and manage John...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            {
                "avatar_url": "portfolio/CraigUtley.webp",
                "name": "Craig Utley",
                "position": "Direct Manager, Consulting",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "There is a right way to come into an organization and John did it the right way...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            {
                "avatar_url": "portfolio/MeredithBean.webp",
                "name": "Meredith Bean",
                "position": "Undergraduate Student",
                "company": "George Mason University",
                "year": "2016",
                "quote": "John was an extraordinary TA to me as a student in an introductory GIS class...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
            {
                "avatar_url": "portfolio/KathrynThorpe.webp",
                "name": "Kathryn Thorpe",
                "position": "Coworker, Customer Success",
                "company": "YellowfinBI",
                "year": "2022",
                "quote": "Not only is John the kind of guy you'd trust with all things IT based on his technical prowess...",
                "link": "https://www.linkedin.com/in/jsolly/",
            },
        ]
        context = super().get_context_data(*args, **kwargs)
        context["url"] = self.request.path
        context["carousel_items"] = carousel_items
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
        return f"<input autofocus='' class='form-control' id='id_gpt_input' maxlength='250' name='gpt_input' required_type='text' value='{safe_completion}'>"

    trigger = request.htmx.trigger

    prompt = prompt_dict[trigger]["prompt"]
    max_tokens = prompt_dict[trigger]["max_tokens"]
    new_content = generate_input_field(prompt, max_tokens)
    return HttpResponse(new_content)


def answer_question_with_GPT(request):
    question = request.POST.get("question-text-area", "")
    completion = answer_question(question=question)
    response = f"<div class='messages__item messages__item--bot'>{completion}</div>"

    return HttpResponse(response)


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
