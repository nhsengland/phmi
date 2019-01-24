import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from roman import fromRoman

from ...models import LawfulBasis, OrgFunction, OrgResponsibility, OrgType


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/reference-material-and-matricies/organisations.csv",
            help="CSV file to load Organisation Functions from",
        )

    def get_function(self, row, org_type, raw_name):
        """
        Build a Function object from the given Org and raw cell

        A function name looks like this:

            2. Underpinning System Activities

        We split that string to get an index and name.
        """
        index, _, name = raw_name.partition(".")
        name = name.strip()

        function, _ = OrgFunction.objects.get_or_create(
            name=name, index=index, type=org_type
        )

        return function

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Import organisations.csv

        The source spreadsheet has been denormalised so the generated CSV
        doesn't have every model in every row.  We use the same pattern for
        each model to handle this.  If the row has a column for a model do a
        get_or_create for it.  Each subsequent lookup assumes the previous
        model exists, relying on Python's loop scope leaking (sorry) to keep
        those variables around through each iteration.

        The only exception to this is how we handle Responsibility's
        lawful_bases field.  A Responsibility can zero -> many Lawful Bases.
        Thus some iterations need to add a LawfulBasis, a Responsibility, Both
        _and_ link them.
        """
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            org_type_name = row["ORGANISATION"]
            if org_type_name:
                cleaned_name = org_type_name[3:].strip()
                slug = slugify(cleaned_name)
                org_type, _ = OrgType.objects.get_or_create(
                    slug=slug, defaults={"name": cleaned_name}
                )

            function_name = row["FUNCTION"]
            if function_name:
                function = self.get_function(row, org_type, function_name)

            lawful_basis_number = row["LAWFUL BASIS NUMBER"]
            lawful_basis_name = row[
                "LAWFUL BASIS FOR SERVICE PROVISION / COMMISSIONING (where applicable)"
            ]
            if lawful_basis_number and lawful_basis_name:
                lawful_basis, _ = LawfulBasis.objects.get_or_create(
                    number=lawful_basis_number, defaults={"name": lawful_basis_name}
                )

            responsibility_name = row["RESPONSIBILITY"]
            if responsibility_name:
                numeral, _, name = responsibility_name.partition(".")
                name = name.strip()
                index = fromRoman(numeral.upper())
                responsibility = OrgResponsibility.objects.create(
                    function=function,
                    name=name,
                    index=index,
                    additional_information=row["ADDITIONAL INFORMATION"],
                    related_reading=row["RELATED READING"],
                )

            if lawful_basis_number and lawful_basis_name:
                responsibility.lawful_bases.add(lawful_basis)
