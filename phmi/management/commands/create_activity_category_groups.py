from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import ActivityCategory, ActivityCategoryGroup, Activity


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        # Secondary data group and catetories
        acg = ActivityCategoryGroup.objects.create(
            name="Secondary data use activities",
            description="Where data is used for purposes other than the individual care of the "
            "patient. Includes activities that contribute to the overall provision "
            "of services to a population as a whole or a group of patients with "
            "a particular condition.",
            index=0,
        )
        (
            ActivityCategory.objects.filter(
                name__istartswith="risk stratification"
            ).update(group=acg, index=4)
        )
        (
            ActivityCategory.objects.filter(
                name__istartswith="managing finances"
            ).update(group=acg, index=1)
        )
        (
            ActivityCategory.objects.filter(
                name__istartswith="planning, implementing and evaluating"
            ).update(group=acg, index=0)
        )

        # Individual care group and catetories
        acg = ActivityCategoryGroup.objects.create(
            name="Individual care",
            description="A clinical, social or public health activity concerned with the "
            "prevention, investigation and treatment of illness and the "
            "alleviation of suffering of individuals.",
            index=1,
        )
        (
            ActivityCategory.objects.filter(
                name__istartswith="activating and empowering"
            ).update(group=acg, index=5)
        )
        (
            ActivityCategory.objects.filter(
                name__istartswith="managing individual"
            ).update(group=acg, index=6)
        )
        (
            ActivityCategory.objects.filter(
                name__istartswith="co-ordinating and optimising"
            ).update(group=acg, index=7)
        )

        # General is no longer ever used, so lets remove it.
        general = "General provision of population health management (including direct care, secondary uses and 'hybrid' activities"
        ActivityCategory.objects.filter(name=general).delete()
        general = "General provision of population health management"
        Activity.objects.filter(name=general).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Created ActivityCategoryGroups and linked to ActivityCategories"
            )
        )
