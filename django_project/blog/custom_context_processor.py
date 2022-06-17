from .models import Category
from django.db.models import Count


def category_renderer(request):
    category_qs = Category.objects.annotate(posts_count=Count('post'))
    try:
        current_category = request.resolver_match.kwargs['category']
    except KeyError:
        current_category = "None"
    return {
        "category_qs": category_qs,
        "current_category": current_category,
    }
