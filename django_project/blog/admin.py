from django.contrib import admin
from .models import Category, Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]


admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
