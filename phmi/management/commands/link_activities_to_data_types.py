import csv
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Activity, DataType
from ...prefix import strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/reference-material-and-matricies/data-map-activity.csv",
            help="CSV file to load Outputs from",
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

                # use column headers to find DataType
                name = strip_prefix(column_header)
                try:
                    data_type = DataType.objects.get(name=name)
                except DataType.DoesNotExist:
                    print(f"Unknown DataType: '{name}'")
                    sys.exit(1)

                data_types.append(data_type)

            # get an Activity for this row
            name = strip_prefix(row["ACTIVITY"])
            try:
                activity = Activity.objects.get(name=name)
            except Activity.DoesNotExist:
                print(f"Unknown Activity: '{name}'")
                sys.exit(1)

            activity.data_types.add(*data_types)

        self.stdout.write(self.style.SUCCESS(f"Linked Activities to DataTypes"))
