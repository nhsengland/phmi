import csv
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import LegalJustification, OrgType

ORG_TYPES = ["CCG", "NHS Trust", "Local Authority", "NHS England"]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path", default="data/csvs/statutes", help="Path to load Statutes from"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        LegalJustification.objects.all().delete()

        for filename in os.listdir(options["path"]):
            with open(os.path.join(options["path"], filename), "r") as f:
                rows = list(csv.reader(f))

            name = filename.replace(".csv", "").replace("-", " ")
            org_type = OrgType.objects.get(name__icontains=name)

            for row in rows:
                lgs = [
                    LegalJustification(name=row[1], details=row[2], org_type=org_type)
                ]
                LegalJustification.objects.bulk_create(lgs)

        self.stdout.write(self.style.SUCCESS(f"Created legal justifications"))
