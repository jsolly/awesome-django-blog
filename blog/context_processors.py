from .models import Category, Post
from django.db.models import Count
from django.urls import resolve
from django.urls import reverse, Resolver404


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
    try:
        match = resolve(request.path_info)
    except Resolver404:
        return {"breadcrumbs": []}
    if match.url_name == "blog-category":
        # Never 404 from a context processor: a missing category already 404s in
        # the view; raising Http404 here turns that into a 500 while rendering
        # the error page (live symptom: leftover /post/... and unknown
        # /category/... slugs).
        category = Category.objects.filter(slug=match.kwargs["slug"]).first()
        if category is None:
            return {"breadcrumbs": breadcrumbs}
        breadcrumbs.append(
            {
                "name": category.name,
                "url": reverse(match.url_name, args=[match.kwargs["slug"]]),
            }
        )
    elif match.url_name == "post-detail":
        post = Post.objects.filter(slug=match.kwargs["slug"]).first()
        if post is None:
            return {"breadcrumbs": breadcrumbs}
        breadcrumbs.append(
            {
                "name": post.category.name,
                "url": reverse("blog-category", args=[post.category.slug]),
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
