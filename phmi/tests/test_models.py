from django.test import TestCase

from phmi import models


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
