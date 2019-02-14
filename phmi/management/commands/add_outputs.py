import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import Output, OutputType


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/reference-material-and-matricies/outputs.csv",
            help="CSV file to load Outputs from",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            _, _, type_name = row["OUTPUT TYPE"].partition(".")
            type_name = type_name.strip()
            if type_name:
                output_type, _ = OutputType.objects.get_or_create(name=type_name)

            _, _, name = row["OUTPUT"].partition(".")
            name = name.strip()

            Output.objects.create(
                type=output_type, name=name, description=row["DESCRIPTION"]
            )

        self.stdout.write(self.style.SUCCESS("Added Outputs"))
