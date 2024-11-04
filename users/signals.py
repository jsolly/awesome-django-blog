from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(instance, created, **kwargs):
    print(f"Post save signal received for user {instance.id}: created={created}")
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(instance, **kwargs):
    instance.profile.save()
