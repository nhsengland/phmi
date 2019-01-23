import csv

from django.core.management.base import BaseCommand

from phmi import models

from ...prefix import strip_prefix

FILE_NAME = "data/csvs/activities.csv"

ROW_MAPPINGS = {
    0: "Activity Category",  # the spreadsheet refers to this as function
    1: "Activity",
    2: "gdpr_condition_for_processing",
    3: "common_law_duty_of_confidence",
    4: "NHS England",
    5: "CCG",
    # Note we are skipping Local Authority(Public Health)
    # and just doing Local Authority(Non-publich Health)
    7: "Local Authority",
    8: "NHS Trust",
    9: "Independent Sector",
    # Note we are ignoring Non NHS-Provider for the time being
}


class Command(BaseCommand):
    def parse_justification_name(self, some_name):
        if "(NHS FT Only)" in some_name:
            return

        pre, suf = some_name.split(":", 1)
        pre = pre.lower().capitalize()
        return f"{pre}:{suf}"

    def handle(self, *args, **options):
        models.Activity.objects.all().delete()
        models.LegalJustification.objects.all().delete()
        with open(FILE_NAME, "r") as f:
            reader = csv.reader(f)
            # skip the first line, its just the headlines
            next(reader)

            activity = None

            for row in reader:
                category_name = strip_prefix(row[0]).capitalize()
                if category_name:
                    category, _ = models.ActivityCategory.objects.get_or_create(
                        name=category_name
                    )

                activity_name = strip_prefix(row[1])
                if activity_name:
                    activity, _ = models.Activity.objects.get_or_create(
                        name=activity_name, defaults={"duty_of_confidence": row[4]}
                    )

                if category_name:
                    category.activities.add(activity)

                for i in range(4, max(ROW_MAPPINGS.keys()) + 1):
                    if i in ROW_MAPPINGS:
                        row_value = row[i].strip()
                        if not row_value:
                            continue

                        print(f"{i} {ROW_MAPPINGS[i]}")
                        org_type = models.OrgType.objects.get(name=ROW_MAPPINGS[i])

                        parsed_justificaiton = self.parse_justification_name(row_value)
                        if not parsed_justificaiton:
                            continue

                        legal_justification, _ = models.LegalJustification.objects.get_or_create(
                            name=self.parse_justification_name(row_value),
                            org_type=org_type,
                        )

                        if activity_name:
                            legal_justification.activities.add(activity)
