from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from phmi import views
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


class TestGroupAdd(AbstractViewsTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("group-add")

    def test_vanilla(self):
        self.client.login(
            email=self.staff_user.email,
            password=PASSWORD
        )
        response = self.client.post(
            self.url,
            dict(
                name="Luton",
                organisations=[self.organisation.id],
                type=self.group_type.id
            )
        )
        expected_url = "/groups/1"
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=200
        )
        care_system = models.CareSystem.objects.get(name="Luton")
        self.assertEqual(
            care_system.type, self.group_type
        )
        self.assertEqual(
            care_system.orgs.get(), self.organisation
        )

    def test_not_is_staff(self):
        self.client.login(
            email=self.normal_user.email,
            password=PASSWORD
        )
        response = self.client.post(
            self.url,
            dict(
                name="Luton",
                organisations=[self.organisation.id],
                type=self.group_type.id
            ),
            follow=True
        )
        self.assertEqual(response.status_code, 403)


class TestGroupEdit(AbstractViewsTestCase):
    def setUp(self):
        super().setUp()
        self.care_system = models.CareSystem.objects.create(
            type=self.group_type,
            name="test_care_system"
        )
        self.url = reverse("group-edit", kwargs=dict(pk=self.care_system.id))

    def test_vanilla(self):
        self.client.login(
            email=self.staff_user.email,
            password=PASSWORD
        )
        response = self.client.post(
            self.url,
            dict(
                name="Luton",
                organisations=[self.organisation.id],
                type=self.group_type.id
            )
        )
        expected_url = "/groups/{}".format(self.care_system.id)
        self.assertRedirects(
            response, expected_url, status_code=302, target_status_code=200
        )
        care_system = models.CareSystem.objects.get(name="Luton")
        self.assertEqual(
            care_system.type, self.group_type
        )
        self.assertEqual(
            care_system.orgs.get(), self.organisation
        )
        self.assertEqual(
            care_system.id, self.care_system.id
        )

    def test_not_is_staff(self):
        self.client.login(
            email=self.normal_user.email,
            password=PASSWORD
        )
        response = self.client.post(
            self.url,
            dict(
                name="Luton",
                organisations=[self.organisation.id],
                type=self.group_type.id
            ),
            follow=True
        )
        self.assertEqual(response.status_code, 403)
