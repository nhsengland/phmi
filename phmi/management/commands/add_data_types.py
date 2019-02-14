import csv

from django.core.management.base import BaseCommand

from ...models import DataCategory, DataType
from ...prefix import strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/reference-material-and-matricies/data-types.csv",
            help="CSV file to load DataTypes from",
        )

    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        categories = {}
        for row in rows:
            category_name = strip_prefix(row["DATA CATEGORY"]).capitalize()

            if not category_name:
                continue

            category = DataCategory(name=category_name)
            categories[category_name] = category
        DataCategory.objects.bulk_create(categories.values())

        types = []
        for row in rows:
            category_name = strip_prefix(row["DATA CATEGORY"]).capitalize()
            if category_name:
                category = categories.get(category_name)

            types.append(
                DataType(
                    name=strip_prefix(row["DATA TYPE"]),
                    example_data_sets=row["EXAMPLE DATA SETS"],
                    category=category,
                )
            )

        DataType.objects.bulk_create(types)

        self.stdout.write(self.style.SUCCESS("Added DataTypes"))
