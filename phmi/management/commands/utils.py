import os
import csv
from django.utils.text import slugify
from django.db.models import Max
from ...models import OrgType, Activity
from ...prefix import normalise_lawful_basis_name


TO_IGNORE = {
    "COMMISSIONING ORGANISATIONS DO NOT POSSESS THE LAWFUL \
BASIS TO UNDERTAKE DIRECT CARE ACTIVITIES",
    'PROVIDER ORGANISATIONS DO NOT POSSESS THE LAWFUL BASIS \
TO UNDERTAKE SECONDARY PURPOSE POPULATION HEALTH MANAGEMENT ACTIVITIES',
    'PROVIDER ORGANISATIONS DO NOT POSSESS THE LAWFUL BASIS TO UNDERTAKE \
SECONDARY PURPOSE POPULATION HEALTH MANAGEMENT RESEARCH'
}


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


def activity_category_index(category_name):
    if category_name in ACTIVITY_CATEGORY_ORDER:
        index = ACTIVITY_CATEGORY_ORDER.index(category_name)
    else:
        max_count = Activity.objects.aggregate(max_index=Max("index"))
        index = max(len(ACTIVITY_CATEGORY_ORDER, max_count))

    print(f"{category_name} {index}")
    return index