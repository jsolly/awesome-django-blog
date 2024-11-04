from django.core.management.base import BaseCommand
from blog.models import Post
from blog.utils import compute_similarity

class Command(BaseCommand):
    help = 'Recalculates the similarity scores for all blog posts.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting similarity score update...'))
        
        for post in Post.objects.all():
            compute_similarity(post.id)
            self.stdout.write(self.style.SUCCESS(f'Updated post {post.id}'))
        
        self.stdout.write(self.style.SUCCESS('All posts have been updated.'))
