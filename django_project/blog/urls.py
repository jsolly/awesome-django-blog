"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    HomeView,
    UserPostListView,
    CreatePostView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CreateCommentView,
    CategoryView,
    post_like_view,
    road_map_view,
    search_view,
    works_cited_view,
)

urlpatterns = [
    path("", HomeView.as_view(), name="blog-home"),
    path("works-cited", works_cited_view, name="blog-works-cited"),
    path("user/<str:username>", UserPostListView.as_view(), name="user-posts"),
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
    path(
        "post/<slug:slug>/comment/", CreateCommentView.as_view(), name="comment-create"
    ),
    path("category/<str:cat>/", CategoryView.as_view(), name="blog-category"),
    path("like/<slug:slug>", post_like_view, name="post-like"),
    path("roadmap/", road_map_view, name="blog-roadmap"),
    path("search/", search_view, name="blog-search"),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
