import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import Activity, ActivityCategory, LegalJustification, OrgType
from ...prefix import normalise_lawful_basis_name, strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/data-map-lawful-basis-relevant.csv",
            help="CSV file to link LegalJustifications and Activities",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["path"], "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            category_name = strip_prefix(row["FUNCTION"]).capitalize()
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

                name = normalise_lawful_basis_name(cell)
                title, _, description = name.partition(": ")
                if title.lower().startswith("provider"):
                    title = title[9:].capitalize()
                if title.lower().startswith("commissioner"):
                    title = title[13:].capitalize()

                lawful_basis = org_type.lawful_bases.get(
                    title=title, description=description
                )

                legal_justification, _ = LegalJustification.objects.get_or_create(
                    activity=activity, org_type=org_type, is_specific=True
                )
                legal_justification.lawful_bases.add(lawful_basis)
        self.stdout.write(
            self.style.SUCCESS("Linked Activities to LegalJustifications")
        )
