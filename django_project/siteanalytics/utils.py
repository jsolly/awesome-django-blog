import ipinfo
from siteanalytics.models import Visitor
from django.contrib.gis.geos import Point


def load_data():
    with open("data/ip_info.csv") as datafile:
        for line in datafile.readlines():
            details = get_IP_details("a", "b")
            location = Point(details.longitude, details.latitude, srid=4326)
            Visitor(
                ip_addr=details.ip,
                country=details.country,
                city=details.city,
                location=location,
            ).save()


def get_IP_details(ip_addr, token):
    handler = ipinfo.getHandler(token)
    return handler.getDetails(ip_addr)
