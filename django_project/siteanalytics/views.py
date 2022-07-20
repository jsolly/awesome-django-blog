# from django.shortcuts import render
from django.shortcuts import render
from .models import Visitor


def leaflet_map_view(request):
    return render(
        request,
        "siteanalytics/leaflet_map.html",
        {"visitors": Visitor.objects.all()},
    )


def openlayers_map_view(request):
    return render(
        request,
        "siteanalytics/openlayers_map.html",
    )


def cesium_map_view(request):
    return render(
        request,
        "siteanalytics/cesium_map.html",
    )


def maplibre_map_view(request):
    return render(
        request,
        "siteanalytics/maplibre_map.html",
    )
