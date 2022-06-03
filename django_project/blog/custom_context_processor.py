from .models import Category
from django.db.models import Count


def category_renderer(request):
    category_qs = Category.objects.annotate(posts_count=Count('post'))
    return {
        "category_qs": category_qs,
    }
