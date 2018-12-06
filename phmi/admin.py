from django.contrib import admin
from django.db.models import TextField
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from phmi import models

admin.site.register(models.CareSystem)
admin.site.register(models.GroupType)
admin.site.register(models.OrgType)
admin.site.register(models.Organisation)
admin.site.register(models.Statute)


class NameSearchAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(models.Activity, NameSearchAdmin)


class StatuteFilter(admin.SimpleListFilter):
    title = 'details'
    parameter_name = 'details'

    def lookups(self, request, model_admin):
        return (
            ('empty', _('Empty')),
            ('populated',  _('Populated')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'empty':
            return queryset.filter(details='')

        if self.value() == 'populated':
            return queryset.exclude(details='')


class StatuteLinkFilter(admin.SimpleListFilter):
    title = 'statute link'
    parameter_name = 'statute_link'

    def lookups(self, request, model_admin):
        return (
            ('empty', _('Empty')),
            ('populated',  _('Populated')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'empty':
            return queryset.filter(statutes=None)

        if self.value() == 'populated':
            return queryset.exclude(statutes=None)


@admin.register(models.LegalJustification)
class LegalJustificationAdmin(admin.ModelAdmin):
    search_fields = ['name', 'details']
    list_filter = (StatuteFilter, StatuteLinkFilter,)


@admin.register(models.User)
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
