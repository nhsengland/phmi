import csv

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ...models import OrgType


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/csvs/org-types.csv",
            help="CSV file to load OrgTypes from",
        )

    def handle(self, *args, **options):
        path = options["file"]
        with open(path, "r") as f:
            data = list(csv.reader(f))

        OrgType.objects.all().delete()

        org_types = [OrgType(name=row[0], slug=slugify(row[0])) for row in data]
        OrgType.objects.bulk_create(org_types)

        self.stdout.write(self.style.SUCCESS(f"Created {len(org_types)} OrgTypes"))
