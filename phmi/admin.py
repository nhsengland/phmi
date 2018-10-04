from django.contrib import admin
from django.db.models import TextField
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _

from .models import CareSystem, GroupType, Organisation, OrgType, User

admin.site.register(CareSystem)
admin.site.register(GroupType)
admin.site.register(OrgType)
admin.site.register(Organisation)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Register our Custom User Model in the admin.

    This configuration is a modified version of Django's UserAdmin from:
    https://github.com/django/django/blob/2.1.2/django/contrib/auth/admin.py
    """

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "care_system",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    filter_horizontal = ("groups", "user_permissions")
    formfield_overrides = {TextField: {"widget": TextInput(attrs={"size": 40})}}
    list_display = ("email", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("email",)
    search_fields = ("email",)
