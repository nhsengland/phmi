import csv
import re
from collections import defaultdict
from phmi import models
from django.db import transaction
from django.core.management.base import BaseCommand, CommandError


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
        result = some_name.replace("(NHS Trust Only)", "")
        pre, suf = some_name.split(":", 1)
        pre = pre.lower().capitalize()
        return f"{pre}:{suf}"

    def parse_activiy_category_name(self, some_name):
        """
        These come in in the form

        A. SOMETHING
        B. SOMETHING ELSE

        lets strip off the `A.` and title case it please
        """
        some_name = some_name.strip().split(" ", 1)[1]
        return some_name.lower().capitalize()

    def clean_activity_name(self, some_name):
        """
        Changes for example "1. An Activitiy" to
        """
        pattern = "^\d+\.\s*"
        return re.sub(pattern, "", some_name)

    def handle(self, *args, **options):
        models.Activity.objects.all().delete()
        models.LegalJustification.objects.all().delete()
        with open(FILE_NAME, "r") as f:
            reader = csv.reader(f)
            # skip the first line, its just the headlines
            next(reader)
            result = defaultdict(list)
            activity = None

            for row in reader:
                if row[0]:
                    category, _ = models.ActivityCategory.objects.get_or_create(
                        name=self.parse_activiy_category_name(row[0])
                    )

                if row[1]:
                    activity, _ = models.Activity.objects.get_or_create(
                        name=self.clean_activity_name(row[1])
                    )
                    activity.duty_of_confidence = row[4]
                    activity.save()

                category.activity_set.add(activity)

                for i in range(4, max(ROW_MAPPINGS.keys())+1):
                    if i in ROW_MAPPINGS:
                        row_value = row[i].strip()
                        if not row_value:
                            continue

                        print(f"{i} {ROW_MAPPINGS[i]}")
                        org_type = models.OrgType.objects.get(
                            name=ROW_MAPPINGS[i]
                        )

                        parsed_justificaiton = self.parse_justification_name(
                            row_value
                        )
                        if not parsed_justificaiton:
                            continue

                        legal_justification, _ = models.LegalJustification.objects.get_or_create(
                            name=self.parse_justification_name(row_value),
                            org_type=org_type
                        )
                        legal_justification.activities.add(
                            activity
                        )


