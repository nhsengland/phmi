import csv
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import (
    Activity,
    LawfulBasis,
    LegalJustification,
    OrgType,
    Statute,
    SubSection,
)
from ...prefix import normalise_lawful_basis_name, strip_prefix

statute_pat = re.compile(r"\((?P<full_text>.*)\)")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/data-map-lawful-basis-relevant.csv",
            help="CSV file to link generate LegalJustification, Statutes, and SubSections",
        )

    def build_org_types(self, rows):
        """Build Org Type names from the header keys of the loaded CSV."""
        first = rows[0]
        org_types = list(first.keys())[4:]
        org_types = [o for o in org_types if o]
        org_types = {
            o: OrgType.objects.get(slug__startswith=slugify(o)) for o in org_types
        }
        return org_types

    @transaction.atomic
    def handle(self, *args, **options):
        LegalJustification.objects.all().delete()
        Statute.objects.all().delete()
        SubSection.objects.all().delete()

        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        org_types = self.build_org_types(rows)

        for row in rows:
            activity_name = strip_prefix(row["ACTIVITY"])
            if activity_name:
                activity, created = Activity.objects.get_or_create(
                    name=activity_name,
                    defaults={
                        "duty_of_confidence": row["Common Law Duty of Confidence"]
                    },
                )
                if created:
                    print(f"Created Activity: {activity.name}")

            for name, org_type in org_types.items():
                lawful_basis_name = row[name]
                if not lawful_basis_name:
                    continue

                lawful_basis_name = normalise_lawful_basis_name(lawful_basis_name)
                title, _, description = lawful_basis_name.partition(": ")
                lawful_basis = LawfulBasis.objects.filter(
                    title=title, description=description, org_type=org_type
                )

                lj, _ = LegalJustification.objects.get_or_create(
                    activity=activity, org_type=org_type, is_specific=True
                )
                lj.lawful_bases.add(*lawful_basis)

        self.stdout.write(self.style.SUCCESS("Added LegalJustifications"))
