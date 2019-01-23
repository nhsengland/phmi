import csv

from django.core.management.base import BaseCommand

from ...models import GroupType


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/csvs/group-types.csv",
            help="CSV file to load GroupTypes from",
        )

    def handle(self, *args, **options):
        path = options["file"]

        with open(path, "r") as f:
            data = csv.reader(f)
            group_types = [GroupType(name=row[0]) for row in data]

        GroupType.objects.bulk_create(group_types)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(group_types)} GroupTypes")
        )
