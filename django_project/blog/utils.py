from django.utils.text import slugify

def slugify_instance_title(instance, save=False, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    instance.slug = slug
    if save:
        instance.save()


def get_client_ip(request):
    x_forward_for = request.META.get("HTTP_X_FORWARD_FOR")

    if x_forward_for:
        ip = x_forward_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_post_like_status(request, post):
    ip = get_client_ip(request)
    if post.likes.filter(ip=ip).exists():
        return True
    return False




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