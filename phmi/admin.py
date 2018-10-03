from django.contrib import admin

from .models import CareSystem, GroupType, Organisation, OrgType

admin.site.register(CareSystem)
admin.site.register(GroupType)
admin.site.register(OrgType)
admin.site.register(Organisation)
