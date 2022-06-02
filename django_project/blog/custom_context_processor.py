from .models import Category
from django.db.models import Count


def category_renderer(request):
    # cat_list = Category.objects.all()
    cat_list = Category.objects.annotate(posts_count=Count('post'))
    return {
        "cat_list": cat_list,
    }
