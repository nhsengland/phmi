import csv
import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import LegalJustification, OrgType
from ...prefix import normalise_justification_name


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

            slug = slugify(filename.replace(".csv", ""))
            org_type = OrgType.objects.get(slug=slug)

            for row in rows:
                name = normalise_justification_name(row[1])
                lg, _ = LegalJustification.objects.get_or_create(
                    name=name, defaults={"details": row[2]}
                )
                lg.org_types.add(org_type)

        self.stdout.write(self.style.SUCCESS("Added LegalJustifications"))
