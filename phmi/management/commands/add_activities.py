import csv

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from ...models import Activity, ActivityCategory
from ...prefix import strip_prefix


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/csvs/activities.csv",
            help="CSV file to load Activities from",
        )

    def handle(self, *args, **options):
        with open(options["path"], "r") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            category_name = strip_prefix(row["FUNCTION"]).capitalize()
            if category_name:
                category, _ = ActivityCategory.objects.get_or_create(
                    name=category_name, slug=slugify(category_name)[:50]
                )

            name = strip_prefix(row["ACTIVITY"])
            Activity.objects.create(
                name=name, slug=slugify(name)[:50], activity_category=category
            )

        self.stdout.write(self.style.SUCCESS("Added Activities"))
