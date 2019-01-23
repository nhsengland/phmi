from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import ActivityCategory, ActivityCategoryGroup


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        # Secondary data group and catetories
        acg = ActivityCategoryGroup.objects.create(
            name="Secondary data use activities",
            description="Where data is used for purposes other than the individual care of the"
            "patient. Includes activities that contribute to the overall provision"
            "of services to a population as a whole or a group of patients with"
            "a particular condition.",
            index=0,
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="Risk stratification"
            ).update(group=acg, index=0)
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="Managing finances"
            ).update(group=acg, index=1)
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="Planning, implementing and evaluating"
            ).update(group=acg, index=2)
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="General Provision of Population"
            ).update(group=acg, index=3)
        )

        # Individual care group and catetories
        acg = ActivityCategoryGroup.objects.create(
            name="Individual care",
            description="A clinical, social or public health activity concerned with the"
            "prevention, investigation and treatment of illness and the"
            "alleviation of suffering of individuals.",
            index=0,
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="Activating and empowering"
            ).update(group=acg, index=4)
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="Managing individual"
            ).update(group=acg, index=5)
        )
        (
            ActivityCategory.objects.filter(
                name__startswith="Co-ordinating and optimising"
            ).update(group=acg, index=6)
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created ActivityCategoryGroups and linked to ActivityCategories"
            )
        )
