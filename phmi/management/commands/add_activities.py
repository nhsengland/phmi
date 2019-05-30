import csv

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db.models import Max

from ...models import Activity, ActivityCategory
from ...prefix import strip_prefix
from .utils import activity_category_index


ACTIVITY_CATEGORY_ORDER = [
    "Planning, implementing and evaluating population health strategy",
    "Managing finances, quality and outcomes",
    "General provision of population health management (including direct care, secondary uses and 'hybrid' activities)",
    "Risk stratification for early intervention and prevention",
    "Activating and empowering citizens",
    "Co-ordinating and optimising service user flows",
    "Managing individual care",
    "Undertaking research",
]


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
                index = activity_category_index(category_name)
                category, _ = ActivityCategory.objects.get_or_create(
                    name=category_name, slug=slugify(category_name)[:50],
                    index=index
                )

            name = strip_prefix(row["ACTIVITY"])
            Activity.objects.create(
                name=name, slug=slugify(name)[:50], activity_category=category
            )

        self.stdout.write(self.style.SUCCESS("Added Activities"))
