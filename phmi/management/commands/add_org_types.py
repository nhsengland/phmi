import csv
import os

from django.core.management.base import BaseCommand, CommandError

from ...models import OrgType


class Command(BaseCommand):
    help = "Load OrgTypes from the given CSV"

    def add_arguments(self, parser):
        parser.add_argument("file", help="CSV file to load OrgTypes from")

    def handle(self, *args, **options):
        path = options["file"]
        if not os.path.exists(path):
            raise CommandError(f"Unknown path: {path}")

        with open(path, "r") as f:
            data = csv.reader(f)
            org_types = [OrgType(name=row[0]) for row in data]

        OrgType.objects.bulk_create(org_types)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(org_types)} OrgTypes")
        )
