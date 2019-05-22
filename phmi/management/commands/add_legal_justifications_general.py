import csv
import re
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.utils.functional import cached_property
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
from . import utils

STATUTES_PATH = "data/csvs/statutes"
LAWFUL_BASIS_PATH = "data/csvs/data-map-lawful-basis-general.csv"


statute_pat = re.compile(r"\((?P<full_text>.*)\)")


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

    @cached_property
    def legal_basis_map(self):
        """
        returns a map of org_type -> number -> legal_basis
        """
        result = defaultdict(dict)
        for row in utils.iter_statutes(STATUTES_PATH):
            org_type, number, name, title, description, details = row
            result[org_type][number] = LawfulBasis.objects.filter(
                title=title, description=description, org_type=org_type
            )
        return result

    @transaction.atomic
    def handle(self, *args, **options):
        Statute.objects.all().delete()
        SubSection.objects.all().delete()

        with open(LAWFUL_BASIS_PATH, "r") as f:
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
                if not row[name].strip() or row[name].strip() in utils.TO_IGNORE:
                    continue
                lawful_basis_name = row[name]

                # The id as it appears on the spreadsheet
                lawful_basis_spreadsheet_id = int(lawful_basis_name)
                lawful_basis = self.legal_basis_map[org_type][lawful_basis_spreadsheet_id]
                lj, _ = LegalJustification.objects.get_or_create(
                    activity=activity, org_type=org_type, is_specific=False
                )
                lj.lawful_bases.add(*lawful_basis)

        self.stdout.write(self.style.SUCCESS("Added General Legal Justifications"))
