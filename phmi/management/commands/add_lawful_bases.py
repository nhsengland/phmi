import csv
import os
import re
import sys

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from more_itertools import chunked

from ...models import LawfulBasis, OrgType, Statute, SubSection
from ...prefix import normalise_lawful_basis_name

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
        for name in os.listdir(options["path"]):
            with open(os.path.join(options["path"], name), "r") as f:
                rows = list(csv.reader(f))

            org_type_slug_ish, _ = os.path.splitext(name)
            org_type = OrgType.objects.get(slug__startswith=slugify(org_type_slug_ish))

            for row in rows:
                if row[0].strip() == TO_IGNORE:
                    continue
                name = normalise_lawful_basis_name(row[1])
                title, _, description = name.partition(": ")

                try:
                    subsections = list(self.iter_subsections(row[2]))
                except Exception as e:
                    print(f"OrgType: {org_type.name} | {e}")
                    sys.exit(1)

                lawful_basis, _ = LawfulBasis.objects.get_or_create(
                    org_type=org_type,
                    title=title,
                    description=description,
                    details=row[2],
                )
                lawful_basis.subsections.add(*subsections)

        self.stdout.write(
            self.style.SUCCESS("Added Lawful Bases, Subsections, & Statutes")
        )
