from django.db import IntegrityError
import ipinfo
from django.contrib.gis.geos import fromstr
import csv
import os
from siteanalytics.models import Visitor


def get_IP_details(ip_addr, token):
    handler = ipinfo.getHandler(token)
    return handler.getDetails(ip_addr)


def load_data():
    with open("ip_info_small.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            details = get_IP_details(row["ip"], os.environ["IP_INFO_TOKEN"])
            try:
                location = fromstr(
                    f"POINT({details.longitude} {details.latitude})", srid=4326
                )
            except Exception as e:
                print(f"I had trouble parsing row {row['id']}")
                print(e)
                continue
            try:
                Visitor(
                    ip_addr=details.ip,
                    country=details.country,
                    city=details.city,
                    location=location,
                ).save()
            except IntegrityError:  # happens with duplicate IPs
                pass


if __name__ == "__main__":
    load_data()
