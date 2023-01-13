from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .feeds import blogFeed, atomFeed
from .views import (
    HomeView,
    CreatePostView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CategoryView,
    search_view,
    AllPostsView,
)

urlpatterns = [
    path("rss/", blogFeed(), name="rss"),
    path('atom/', atomFeed(), name='atom'),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", HomeView.as_view(), name="home"),
    path("all-posts/", AllPostsView.as_view(), name="all-posts"),
    path("post/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
    path("post/new", CreatePostView.as_view(), name="post-create"),
    path(
        "post/<slug:slug>/",
        include(
            [
                path("update", PostUpdateView.as_view(), name="post-update"),
                path("delete", PostDeleteView.as_view(), name="post-delete"),
            ]
        ),
    ),
    path("category/<str:category>/", CategoryView.as_view(), name="blog-category"),
    path("search/", search_view, name="blog-search"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
