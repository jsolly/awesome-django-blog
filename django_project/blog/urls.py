from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from .feeds import blogFeed, atomFeed
from .views import (
    HomeView,
    CreatePostView,
    CommentUpdateView,
    delete_comment,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CategoryView,
    PortfolioView,
    AllPostsView,
    SearchView,
    StatusView,
    generate_gpt_input_value,
    answer_question_with_GPT,
)

urlpatterns = [
    path("status/", cache_page(60)(StatusView.as_view()), name="status"),
    path("answer-with-gpt/", answer_question_with_GPT, name="answer-with-gpt"),
    path(
        "generate-with-gpt/<int:post_id>/",
        generate_gpt_input_value,
        name="generate-with-gpt",
    ),
    path("rss/", blogFeed(), name="rss"),
    path("atom/", atomFeed(), name="atom"),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", HomeView.as_view(), name="home"),
    path("all-posts/", AllPostsView.as_view(), name="all-posts"),
    path("post/new", CreatePostView.as_view(), name="post-create"),
    path("post/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
    path("post/<slug:slug>/update", PostUpdateView.as_view(), name="post-update"),
    path("post/<slug:slug>/delete", PostDeleteView.as_view(), name="post-delete"),
    path("category/<slug:slug>/", CategoryView.as_view(), name="blog-category"),
    path("portfolio/", PortfolioView.as_view(), name="portfolio"),
    path("search/", SearchView.as_view(), name="blog-search"),
    path("comment/<int:pk>/update", CommentUpdateView.as_view(), name="comment-update"),
    path("comment/<int:pk>/delete", delete_comment, name="comment-delete"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
