from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        default="default.webp",
        upload_to="profile_pics",
        storage=default_storage,
    )

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_absolute_url(self):
        return reverse("profile")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Skip processing for default image
        if self.image.name == "default.webp":
            return

        if str(os.environ.get("USE_S3")).lower() == "true":
            try:
                img_read = default_storage.open(self.image.name, "rb")
                img = Image.open(img_read)

                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)

                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    default_storage.save(self.image.name, ContentFile(buffer.getvalue()))
            except FileNotFoundError:
                # Handle the error or just pass if using default image
                pass
        else:
            with Image.open(self.image.path) as img:
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
