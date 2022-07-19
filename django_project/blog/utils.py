from django.utils.text import slugify


def slugify_instance_title(instance, save=False, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    instance.slug = slug
    if save:
        instance.save()


# def post_pre_save(sender, instance, *args, **kwargs):
#     print("pre_save")
#     if instance.slug is None:
#         slugify_instance_title(instance)

# pre_save.connect(post_pre_save, sender=Post)

# def post_post_save(sender, instance, created, *args, **kwargs):
#     print("post_save")
#     if created:
#         slugify_instance_title(instance, save=True)

# post_save.connect(post_post_save, sender=Post)
