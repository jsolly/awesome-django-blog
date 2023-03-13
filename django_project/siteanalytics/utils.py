import ipinfo
from django.contrib.gis.geos import fromstr
import csv
import os
from siteanalytics.models import Visitor
import logging
from requests.exceptions import HTTPError

logger = logging.getLogger("django")


def load_data(file_path):  # pragma: no cover
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ip_addr = row["ip"]
            if ip_addr in ("127.0.0.1"):
                continue
            try:
                Visitor.objects.get(ip_addr=ip_addr)
                continue  # If it exists, go to the next one
            except Visitor.DoesNotExist:
                pass
            try:
                handler = ipinfo.getHandler(os.environ["IP_INFO_TOKEN"])
                details = handler.getDetails(row["ip"])
            except HTTPError:
                logger.info(f"IP info couldn't find IP addres:{ip_addr}")
                continue  # pinfo couldn't find it
            location = fromstr(
                f"POINT({details.longitude} {details.latitude})", srid=4326
            )

            Visitor(
                ip_addr=details.ip,
                country=details.country,
                city=details.city,
                location=location,
            ).save()


def get_client_ip(request):
    ip_addr = request.META.get("HTTP_CF_CONNECTING_IP")
    if ip_addr:
        return ip_addr
    x_forward_for = request.META.get("HTTP_X_FORWARD_FOR")
    if x_forward_for:
        return request.META.get("HTTP_X_FORWARD_FOR").split(",")[0]

    ip_addr = request.META.get("REMOTE_ADDR")
    if ip_addr:
        return ip_addr


def add_visitor_if_not_exist(request):
    ip_addr = get_client_ip(request)
    if not ip_addr:
        logger.info("Couldn't find IP address")
        return
    if ip_addr in ("127.0.0.1"):
        return
    try:
        Visitor.objects.get(ip_addr=ip_addr)
        return
    except Visitor.DoesNotExist:
        try:
            handler = ipinfo.getHandler(os.environ["IP_INFO_TOKEN"])
            details = handler.getDetails(ip_addr)
        except HTTPError:
            logger.info(f"IP info couldn't find IP addres:{ip_addr}")
            return

        location = fromstr(f"POINT({details.longitude} {details.latitude})", srid=4326)

        return Visitor.objects.create(
            ip_addr=details.ip,
            country=details.country,
            city=details.city,
            location=location,
        )
