import ipinfo
from django.contrib.gis.geos import fromstr
import csv
import os
from siteanalytics.models import Visitor
import logging

logger = logging.getLogger("django")


def load_data(file_path):
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                Visitor.objects.get(ip_addr=row["ip"])
                continue  # If it exists, go to the next one
            except Visitor.DoesNotExist:
                pass
            handler = ipinfo.getHandler(os.environ["IP_INFO_TOKEN"])
            details = handler.getDetails(row["ip"])
            try:
                location = fromstr(
                    f"POINT({details.longitude} {details.latitude})", srid=4326
                )
            except Exception as e:
                print(f"I had trouble parsing row {row['id']}")
                print(e)
                continue

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
    else:
        return None


def add_ip_person_if_not_exist(request):
    ip_addr = get_client_ip(request)
    if not ip_addr:
        return
    try:
        Visitor.objects.get(ip_addr=ip_addr)
        logger.info("Visitor already exists")
        return
    except Visitor.DoesNotExist:
        logger.info(f"IP address {ip_addr} is not an existing visitor")
        handler = ipinfo.getHandler(os.environ["IP_INFO_TOKEN"])
        details = handler.getDetails(ip_addr)
        try:
            location = fromstr(
                f"POINT({details.longitude} {details.latitude})", srid=4326
            )
        except Exception:
            logger.warning(f"I had trouble parsing {ip_addr}")
            return
        logger.info(f"I am about to add {ip_addr} as a visitor")
        return Visitor.objects.create(
            ip_addr=details.ip,
            country=details.country,
            city=details.city,
            location=location,
        )
