from collections import defaultdict, OrderedDict
from django.shortcuts import render
from django.urls import reverse
from django.core import signing
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.functional import cached_property
from django.views.generic import (
    TemplateView,
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from phmi import models


class AbstractProjectView(TemplateView):
    def decode_location_sign(self):
        if "location_sign" not in self.kwargs:
            return {}

        location_dict = signing.loads(self.kwargs["location_sign"])
        location_dict["care_system"] = get_object_or_404(
            models.CareSystem,
            id=location_dict["care_system"]
        )
        return location_dict

    def decode_activity_sign(self):
        if "activity_sign" not in self.kwargs:
            return {}
        activity_ids = signing.loads(self.kwargs["activity_sign"])[
            "activities"
        ]
        return dict(
            project_activities=models.Activity.objects.filter(
                id__in=activity_ids
            )
        )

    @cached_property
    def activities(self):
        return models.Activity.objects.all()

    @cached_property
    def care_systems(self):
        return models.CareSystem.objects.all()

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update(self.decode_location_sign())
        ctx.update(self.decode_activity_sign())
        return ctx


class Home(TemplateView):
    template_name = "home.html"


class ProjectLocationView(AbstractProjectView):
    template_name = "projects/location.html"

    def post(self, *args, **kwargs):
        care_system = get_object_or_404(
            models.CareSystem,
            id=self.request.POST["care_system"]
        )
        governance = self.request.POST["governance"]
        project_name = self.request.POST["project_name"]
        location_sign = signing.dumps(dict(
            care_system=care_system.id,
            governance=governance,
            project_name=project_name
        ))
        return HttpResponseRedirect(
            reverse("project-activity", kwargs=dict(
                location_sign=location_sign
            ))
        )


class ProjectActivityView(AbstractProjectView):
    template_name = "projects/activity.html"

    def post(self, *args, **kwargs):
        activity_ids = [int(i) for i in self.request.POST.getlist("activities")]
        activities = models.Activity.objects.filter(id__in=activity_ids)
        if activities.count() < len(activities):
            raise Http404("Unable to find all the activities")
        activity_sign = signing.dumps(dict(
            activities=activity_ids
        ))
        return HttpResponseRedirect(
            reverse("project-result", kwargs=dict(
                location_sign=self.kwargs["location_sign"],
                activity_sign=activity_sign
            ))
        )


class ProjectResultView(AbstractProjectView):
    template_name = "projects/result.html"

    def get_org_by_activity(self, care_system, project_activities):
        org_types = models.OrgType.objects.filter(
            orgs__care_system=care_system
        ).distinct()
        return models.LegalJustification.objects.by_org_and_activity(
            care_system.orgs.all(), project_activities
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["by_org_and_activity"] = self.get_org_by_activity(
            ctx["care_system"], ctx["project_activities"]
        )
        ctx["justified_orgs"] = [
            i for i, v in ctx["by_org_and_activity"].items() if all(v.values())
        ]
        return ctx
