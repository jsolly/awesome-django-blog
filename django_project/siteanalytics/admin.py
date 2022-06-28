from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Visitor


@admin.register(Visitor)
class VisitorAdmin(OSMGeoAdmin):
    list_display = ("ip_addr", "location", "city", "country")
