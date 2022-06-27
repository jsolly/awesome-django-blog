import ipinfo
from siteanalytics.models import Visitor
from django.contrib.gis.geos import Point


def get_IP_details(ip_addr, token):
    handler = ipinfo.getHandler(token)
    return handler.getDetails(ip_addr)
