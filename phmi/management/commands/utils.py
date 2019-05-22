import os
import csv
from django.utils.text import slugify
from ...models import OrgType
from ...prefix import normalise_lawful_basis_name


TO_IGNORE = {
    "COMMISSIONING ORGANISATIONS DO NOT POSSESS THE LAWFUL \
BASIS TO UNDERTAKE DIRECT CARE ACTIVITIES",
    'PROVIDER ORGANISATIONS DO NOT POSSESS THE LAWFUL BASIS \
TO UNDERTAKE SECONDARY PURPOSE POPULATION HEALTH MANAGEMENT ACTIVITIES',
    'PROVIDER ORGANISATIONS DO NOT POSSESS THE LAWFUL BASIS TO UNDERTAKE \
SECONDARY PURPOSE POPULATION HEALTH MANAGEMENT RESEARCH'
}


def iter_statutes(path=None):
    for name in os.listdir(path):
        with open(os.path.join(path, name), "r") as f:
            rows = list(csv.reader(f))

        org_type_slug_ish, _ = os.path.splitext(name)
        org_type = OrgType.objects.get(
            slug__startswith=slugify(org_type_slug_ish)
        )
        for row in rows:
            if not row[0].strip() or row[0].strip() in TO_IGNORE:
                continue
            number = row[0]
            name = normalise_lawful_basis_name(row[1])
            title, _, description = name.partition(": ")
            details = row[2]

            yield org_type, int(number), name, title, description, details
