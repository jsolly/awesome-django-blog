from django.contrib.gis.db import models


class Visitor(models.Model):
    ip_addr = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    location = models.PointField()

    def __str__(self):
        return self.ip_addr
