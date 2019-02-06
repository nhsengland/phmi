import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import Activity, ActivityCategory, LegalJustification, OrgType
from ...prefix import normalise_justification_name, strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/data-map-legal-basis.csv",
            help="CSV file to link LegalJustifications and Activities",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            # there is a BOM (byte order mark) character on the first line of
            # this CSV, hence the unicode character in the row title here.
            category_name = strip_prefix(row["\ufeffFUNCTION"]).capitalize()
            if category_name:
                category, _ = ActivityCategory.objects.get_or_create(name=category_name)

            activity_name = strip_prefix(row["ACTIVITY"])
            if activity_name:
                activity, _ = Activity.objects.get_or_create(
                    name=activity_name,
                    defaults={
                        "duty_of_confidence": row["Common Law Duty of Confidence"]
                    },
                )

            category.activities.add(activity)

            for column_header in list(row.keys())[4:]:
                if not column_header:
                    continue

                slug = slugify(column_header)
                org_type = OrgType.objects.get(slug__startswith=slug)

                cell = row[column_header]

                if not cell:
                    continue

                justification_name = normalise_justification_name(cell)
                legal_justification, _ = LegalJustification.objects.get_or_create(
                    name=justification_name
                )
                legal_justification.activities.add(activity)
                legal_justification.org_types.add(org_type)

        self.stdout.write(
            self.style.SUCCESS("Linked Activities to LegalJustifications")
        )
