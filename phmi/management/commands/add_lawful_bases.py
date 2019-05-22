import re
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from more_itertools import chunked

from . import utils
from ...models import LawfulBasis, Statute, SubSection


statute_pat = re.compile(r"\((?P<full_text>.*)\)")

TO_IGNORE = "COMMISSIONING ORGANISATIONS DO NOT POSSESS THE LAWFUL \
BASIS TO UNDERTAKE DIRECT CARE ACTIVITIES"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--path", default="data/csvs/statutes", help="")

    def iter_subsections(self, text):
        match = statute_pat.search(text.replace("\n", " "))
        if not match:
            raise Exception(f"unexpected statute: {text}")

        pointers = match.group("full_text")

        subsections = list(chunked((s.strip() for s in pointers.split(",")), 2))

        for maybe_subsection in subsections:
            try:
                statute, subsection = maybe_subsection
            except ValueError:
                print(
                    f"Could not pull Statute/Subsection from: {' '.join(maybe_subsection)}"
                )
                continue

            statute, _ = Statute.objects.get_or_create(name=statute)
            subsection, _ = SubSection.objects.get_or_create(
                statute=statute, name=subsection
            )
            yield subsection

    @transaction.atomic
    def handle(self, *args, **options):
        for row in utils.iter_statutes(options["path"]):
            org_type, _, name, title, description, details = row

            try:
                subsections = list(self.iter_subsections(details))
            except Exception as e:
                print(f"OrgType: {org_type.name} | {e}")
                sys.exit(1)

            lawful_basis, _ = LawfulBasis.objects.get_or_create(
                org_type=org_type,
                title=title,
                description=description,
                details=details,
            )
            lawful_basis.subsections.add(*subsections)

        self.stdout.write(
            self.style.SUCCESS("Added Lawful Bases, Subsections, & Statutes")
        )
