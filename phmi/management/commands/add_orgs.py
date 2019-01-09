import csv
import os

from django.core.management.base import BaseCommand, CommandError

from ...models import Organisation, OrgType

ORG_CSVS = [
    "ccg", "csu", "dscro", "independent-sector",
    "local-authority", "nhs-trust"

]


class Command(BaseCommand):
    help = "Load Organisations"

    def build_organisations(self, data, org_type):
        for row in data:
            try:
                ods_code = row[1]
            except IndexError:
                ods_code = None

            yield Organisation(name=row[0], ods_code=ods_code, type=org_type)

    def get_type(self, csv_name):
        """
        We expect an org type csv to be a case insensitive
        version of an org type.

        Org types should already have been loaded.
        """
        return OrgType.objects.get(
            name__iexact=csv_name.replace("-", " ")
        )

    def handle(self, *args, **options):

        org_types = OrgType.objects.all()
        if len(org_types) < 1:
            raise CommandError("No OrgTypes found, try running add_org_types first.")

        for csv_name in ORG_CSVS:
            path = f"data/csvs/{csv_name}.csv"
            if not os.path.exists(path):
                raise CommandError(f"Unknown path: {path}")

            org_type = self.get_type(csv_name)

            with open(path, "r") as f:
                data = csv.reader(f)
                organisations = list(self.build_organisations(data, org_type))

            Organisation.objects.bulk_create(organisations)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(organisations)} Organisations"
                )
            )
