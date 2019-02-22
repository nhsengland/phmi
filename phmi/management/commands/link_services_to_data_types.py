import csv
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import DataType, Service
from ...prefix import strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/data-map-service.csv",
            help="CSV file to link Services to DataTypes from",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            data_types = []

            # use column headers to find DataTypes
            for column_header in list(row.keys())[1:]:
                if row[column_header] != "✓":
                    continue

                name = strip_prefix(column_header)
                try:
                    data_type = DataType.objects.get(name=name)
                except DataType.DoesNotExist:
                    print(f"Unknown DataType: '{name}'")
                    sys.exit(1)

                data_types.append(data_type)

            # get a Service for this row
            name = strip_prefix(row["SERVICE"]).capitalize()
            service, _ = Service.objects.get_or_create(name=name, slug=slugify(name))

            service.data_types.add(*data_types)

        self.stdout.write(self.style.SUCCESS(f"Linked Services to DataTypes"))
