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

TO_IGNORE = "COMMISSIONING ORGANISATIONS DO NOT POSSESS THE LAWFUL BASIS TO UNDERTAKE DIRECT CARE ACTIVITIES"

DUTY_OF_CONFIDENCE_TRANSLATE = {
    "Implied consent/reasonable expectations":
        "Implied consent/reasonable expectations or pseudo/anon data where it doesn't apply"
}

statute_pat = re.compile(r"\((?P<full_text>.*)\)")


LAWFUL_BASIS_PATH = "data/csvs/data-map-lawful-basis-relevant.csv"


class Command(BaseCommand):
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
        Statute.objects.all().delete()
        SubSection.objects.all().delete()

        with open(LAWFUL_BASIS_PATH, "r") as f:
            rows = list(csv.DictReader(f))

        org_types = self.build_org_types(rows)
        duty_of_confidence = ""
        for row in rows:
            activity_name = strip_prefix(row["ACTIVITY"])
            # duty of confidence uses the last populated duty of confidence
            # some of the rows are empty, in that case, use the last populated
            # duty of confidence as that's how the excel spread sheet renders
            if row["Common Law Duty of Confidence"]:
                duty_of_confidence = row["Common Law Duty of Confidence"].strip()
                # There's a typo in the provided data for duty of
                # confidence, this fixes
                if duty_of_confidence in DUTY_OF_CONFIDENCE_TRANSLATE:
                    duty_of_confidence = DUTY_OF_CONFIDENCE_TRANSLATE.get(duty_of_confidence)
            if activity_name:
                activity, created = Activity.objects.update_or_create(
                    name=activity_name,
                    defaults={
                        "duty_of_confidence": duty_of_confidence
                    },
                )
                if created:
                    print(f"Created Activity: {activity.name}")

            for name, org_type in org_types.items():
                lawful_basis_name = row[name]
                if not lawful_basis_name or lawful_basis_name == TO_IGNORE:
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

        self.stdout.write(self.style.SUCCESS("Added Relevant Legal Justifications"))
