from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Visitor


@admin.register(Visitor)
class VisitorAdmin(GISModelAdmin):
    list_display = ("ip_addr", "location", "city", "country")
