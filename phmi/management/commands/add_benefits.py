import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Benefit, BenefitAim


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/reference-material-and-matricies/benefits.csv",
            help="CSV file to load Benefits from",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            aim_name = row["AIM"]
            if aim_name:
                aim, _ = BenefitAim.objects.get_or_create(name=aim_name)

            index, _, name = row["BENEFIT"].partition(".")
            name = name.strip()

            Benefit.objects.create(aim=aim, name=name, index=index)

        self.stdout.write(self.style.SUCCESS("Added Benefits"))
