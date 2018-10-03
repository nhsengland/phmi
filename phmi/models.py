"""
Group: The Black Country and West Birmingham STP
GroupType: STP
Org: Dudley CCG
OrgType: CCG
"""

from django.db import models


class CareSystem(models.Model):
    type = models.ForeignKey(
        "GroupType", on_delete=models.CASCADE, related_name="care_systems"
    )

    name = models.TextField()

    class Meta:
        unique_together = ("type", "name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("group-detail", args=[str(self.id)])


class GroupType(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class OrgType(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Organisation(models.Model):
    care_system = models.ManyToManyField("CareSystem", related_name="orgs")
    type = models.ForeignKey("OrgType", on_delete=models.CASCADE, related_name="orgs")

    name = models.TextField()
    ods_code = models.TextField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
