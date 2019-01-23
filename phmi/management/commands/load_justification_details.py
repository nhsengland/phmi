import csv
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import LegalJustification, OrgType

ORG_TYPES = ["CCG", "NHS Trust", "Local Authority", "NHS England"]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path", default="data/csvs/statutes", help="Path to load Statutes from"
        )

    # def get_justifications(self, justification_activity, org_type_name):
    #     """
    #     There are some differences in terms of the prefix (e.g. commsissioner
    #     duties vs duties) so we search by the suffix. Then do a match.
    #     """
    #     org_type = models.OrgType.objects.get(name=org_type_name)
    #     prefix, justification_suffix = justification_activity.split(":", 1)

    #     legal_justification = models.LegalJustification.objects.filter(
    #         org_type=org_type, name__endswith=justification_suffix
    #     )

    #     result = []
    #     for i in legal_justification:
    #         if prefix.lower() in i.name.split(":")[0].lower():
    #             result.append(i)

    #     if not result:
    #         self.stdout.write(
    #             f"Unable to find {justification_activity} for {org_type_name}"
    #         )
    #         import ipdb

    #         ipdb.set_trace()

    #     return result

    # def create_details(self, org_type_name):
    #     """
    #     Looks for similar names in the details csvs.

    #     Notably the names of duties/powers in the statute have more details

    #     for example they have things such as Comissioner duties rather than
    #     just Duties as it would be called in the details.

    #     As a result we have to do some fiddling to make them
    #     match up.

    #     We can't just use the suffix as for some suffixes there is both
    #     a Duty and a Power
    #     """
    #     file_name = org_type_name.lower().replace(" ", "-")
    #     path = f"data/csvs/statutes/{file_name}.csv"
    #     count = 0

    #     print(f"working on {path}")
    #     with open(path) as f:
    #         reader = csv.reader(f)

    #         for row in reader:
    #             justifications = self.get_justifications(row[1], org_type_name)
    #             for justification in justifications:
    #                 justification.details = row[2]
    #                 justification.save()
    #                 count += 1

    #     return count

    @transaction.atomic
    def handle(self, *args, **options):
        LegalJustification.objects.all().delete()

        for filename in os.listdir(options["path"]):
            with open(os.path.join(options["path"], filename), "r") as f:
                rows = list(csv.reader(f))

            name = filename.replace(".csv", "").replace("-", " ")
            org_type = OrgType.objects.get(name__icontains=name)

            for row in rows:
                lgs = [
                    LegalJustification(name=row[1], details=row[2], org_type=org_type)
                ]
                LegalJustification.objects.bulk_create(lgs)

        self.stdout.write(self.style.SUCCESS(f"Created legal justifications"))
