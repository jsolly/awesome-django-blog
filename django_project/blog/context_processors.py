from .models import Category, Post
from django.db.models import Count
from django.urls import resolve
from django.urls import reverse
from django.shortcuts import get_object_or_404


def category_renderer(request):
    category_qs = Category.objects.annotate(posts_count=Count("post"))
    try:
        current_category = request.resolver_match.kwargs["slug"]
    except (KeyError, AttributeError):
        current_category = "None"
    return {
        "category_qs": category_qs,
        "current_category": current_category,
    }


def breadcrumbs(request):
    breadcrumbs = [{"name": "Home", "url": reverse("home")}]
    match = resolve(request.path_info)
    if match.url_name == "blog-category":
        breadcrumbs.append(
            {
                "name": match.kwargs["slug"],
                "url": reverse(match.url_name, args=[match.kwargs["slug"]]),
            }
        )
    elif match.url_name == "post-detail":
        post = get_object_or_404(Post, slug=match.kwargs["slug"])
        breadcrumbs.append(
            {
                "name": post.category.name,
                "url": reverse("blog-category", args=[post.category.name]),
            }
        )
        breadcrumbs.append(
            {
                "name": post.title,
                "url": reverse(match.url_name, args=[match.kwargs["slug"]]),
            }
        )
    elif match.url_name == "works-cited":
        breadcrumbs.append({"name": "Works Cited", "url": reverse(match.url_name)})
    elif match.url_name == "privacy":
        breadcrumbs.append({"name": "Privacy Policy", "url": reverse(match.url_name)})
    return {"breadcrumbs": breadcrumbs}
