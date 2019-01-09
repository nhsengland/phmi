from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from phmi import models

User = get_user_model()
PASSWORD = "password"


class TestGroupType(TestCase):
    def test_get_display_name_no_parenthesis(self):
        self.assertEqual(
            models.GroupType(name="hello").get_display_name(),
            "hello"
        )

    def test_get_display_name_with_parenthesis(self):
        self.assertEqual(
            models.GroupType(name="hello (h)").get_display_name(),
            "h"
        )


class AbstractViewsTestCase(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            email="staff@nhs.net",
            password=PASSWORD,
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            email="normal@nhs.net",
            password=PASSWORD,
        )
        self.client = Client()
        self.group_type = models.GroupType.objects.create(
            name="Sustainability and transformation partnership (STP)"
        )
        self.org_type = models.OrgType.objects.create(
            name="Acute Trust"
        )
        self.organisation = models.Organisation.objects.create(
            type=self.org_type,
            name="Dunstable Hospital Trust",
            ods_code="111"
        )
