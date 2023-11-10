from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import compute_similarity
from .models import Post


@receiver(post_save, sender=Post)
def trigger_similarity_computation(sender, instance, **kwargs):
    compute_similarity(instance.id)
