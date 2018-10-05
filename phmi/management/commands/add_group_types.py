import csv
import os

from django.core.management.base import BaseCommand, CommandError

from ...models import GroupType


class Command(BaseCommand):
    help = "Load GroupTypes from the given CSV"

    def add_arguments(self, parser):
        parser.add_argument("file", help="CSV file to load GroupTypes from")

    def handle(self, *args, **options):
        path = options["file"]
        if not os.path.exists(path):
            raise CommandError(f"Unknown path: {path}")

        with open(path, "r") as f:
            data = csv.reader(f)
            group_types = [GroupType(name=row[0]) for row in data]

        GroupType.objects.bulk_create(group_types)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(group_types)} GroupTypes")
        )
