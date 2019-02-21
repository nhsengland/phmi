import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from ...models import OrgType
from ...prefix import strip_prefix

nameLUT = {
    "nhs england": "NHS England",
    "ccg": "CCG",
    "local authority (public health)": "Local Authority (Public Health)",
    "local authority (non-public health)": "Local Authority (Non-Public Health)",
    "nhs provider": "NHS Provider",
    "non-nhs provider (inc. charities)": "Non-NHS Provider (inc. Charities)",
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/reference-material-and-matricies/organisations.csv",
            help="CSV file to load Organisation Types from",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Import OrgTypes from organisations.csv

        We need OrgTypes to exist for multiple other objects however there is
        no single Source of Truth for them.  In lieu of a single source the
        author has picked the Organisations sheet to be that source.  This
        command builds OrgTypes from that sheet and nothing else, the other
        objects contained in it are added by another step later.
        """
        with open(options["path"], "r") as f:
            reader = csv.reader(f)
            next(reader)  # skip the header row
            names = [strip_prefix(row[0]) for row in csv.reader(f) if row[0]]

        OrgType.objects.bulk_create(
            OrgType(name=nameLUT[name.lower()], slug=slugify(name)) for name in names
        )

        self.stdout.write(self.style.SUCCESS("Added OrgTypes"))
