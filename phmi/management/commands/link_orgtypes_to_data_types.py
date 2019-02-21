import csv
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import DataType, OrgType
from ...prefix import strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/data-map-org.csv",
            help="CSV file to link Orgs to DataTypes from",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            data_types = []

            for column_header in list(row.keys())[1:]:
                # Only create records for cells with ✓
                if row[column_header] != "✓":
                    continue

                # use column headers to find DataTypes
                name = strip_prefix(column_header)
                try:
                    data_type = DataType.objects.get(name=name)
                except DataType.DoesNotExist:
                    print(f"Unknown DataType: '{name}'")
                    sys.exit(1)

                data_types.append(data_type)

            # get an OrgType for this row
            slug = slugify(strip_prefix(row["ORGANISATION"]))
            try:
                org_type = OrgType.objects.get(slug=slug)
            except OrgType.DoesNotExist:
                print(f"Unknown OrgType slug: '{slug}'")
                sys.exit(1)

            org_type.data_types.add(*data_types)

        self.stdout.write(self.style.SUCCESS(f"Linked OrgTypes to DataTypes"))
