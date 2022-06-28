import ipinfo
from django.contrib.gis.geos import fromstr
import csv
import os
from siteanalytics.models import Visitor


def get_IP_details(ip_addr, token):
    handler = ipinfo.getHandler(token)
    return handler.getDetails(ip_addr)


def load_data(file_path):
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                Visitor.objects.get(ip_addr=row["ip"])
                continue  # If it exists, go to the next one
            except Visitor.DoesNotExist:
                pass
            details = get_IP_details(row["ip"], os.environ["IP_INFO_TOKEN"])
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


if __name__ == "__main__":
    load_data()
