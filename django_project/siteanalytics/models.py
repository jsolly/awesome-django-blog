from django.contrib.gis.db.models import PointField
from django.db import models


class visitor(models.Model):
    ip_addr = (models.CharField(max_length=100),)
    country = (models.CharField(max_length=60),)
    location = PointField()
    timestamp = (models.DateTimeField(),)

    def __str__(self):
        return self.ip_addr
