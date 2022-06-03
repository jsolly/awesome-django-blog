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
    CategoryView,
    road_map_view,
    search_view,
    works_cited_view,
    site_analytics_view
)

urlpatterns = [
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", HomeView.as_view(), name="blog-home"),
    path("works-cited", works_cited_view, name="blog-works-cited"),
    path("site-analytics", site_analytics_view, name="blog-site-analytics"),
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
    path("category/<str:category>/", CategoryView.as_view(), name="blog-category"),
    path("roadmap/", road_map_view, name="blog-roadmap"),
    path("search/", search_view, name="blog-search"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
