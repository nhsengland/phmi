import csv
import os

from django.core.management.base import BaseCommand, CommandError

from ...models import Organisation, OrgType


class Command(BaseCommand):
    help = "Load Organisations from the given CSV"

    def add_arguments(self, parser):
        parser.add_argument("file", help="CSV file to load Organisations from")

    def build_organisations(self, data, org_type):
        for row in data:
            try:
                ods_code = row[1]
            except IndexError:
                ods_code = None

            yield Organisation(name=row[0], ods_code=ods_code, type=org_type)

    def get_type(self, org_types):
        # cast so we can index later
        org_types = list(org_types)

        while True:
            self.stdout.write("Which Organisation Type are you loading in?")
            for i, org_type in enumerate(org_types, start=1):
                self.stdout.write(f" - [{i}] {org_type.name}")
            number = input("Enter a number: ")

            try:
                number = int(number)
            except ValueError:
                self.stderr.write(
                    self.style.ERROR(
                        f"{number} is not a valid number, please try again."
                    )
                )
                continue

            break

        return org_types[number - 1]

    def handle(self, *args, **options):
        path = options["file"]
        if not os.path.exists(path):
            raise CommandError(f"Unknown path: {path}")

        org_types = OrgType.objects.all()
        if len(org_types) < 1:
            raise CommandError("No OrgTypes found, try running add_org_types first.")

        org_type = self.get_type(org_types)

        with open(path, "r") as f:
            data = csv.reader(f)
            organisations = list(self.build_organisations(data, org_type))

        Organisation.objects.bulk_create(organisations)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(organisations)} Organisations"
            )
        )
