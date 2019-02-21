import csv

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from phmi.prefix import strip_prefix


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("statutes.csv", "r") as f:
            rows = csv.reader(f)
            headers = next(rows)
            rows = list(rows)

        org_types = [slugify(strip_prefix(h).replace("\n", " ")) for h in headers if h]

        for i, org_type in enumerate(org_types, start=1):
            with open(f"data/csvs/statutes/{org_type}.csv", "w") as f:
                writer = csv.writer(f)
                for row in rows:
                    start = (i * 4) - 4
                    end = (i * 4) - 1
                    cells = row[start:end]

                    if not all(cells):
                        continue

                    writer.writerow(cells)
