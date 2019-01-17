from django.core import signing
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from phmi import models
from phmi import views as phmi_views


class AbstractProjectView(phmi_views.AbstractPhmiView, TemplateView):
    def decode_location_sign(self):
        if "location_sign" not in self.kwargs:
            return {}

        location_dict = signing.loads(self.kwargs["location_sign"])
        return location_dict

    def decode_activity_sign(self):
        if "activity_sign" not in self.kwargs:
            return {}
        activity_ids = signing.loads(self.kwargs["activity_sign"])["activities"]
        return dict(activities=models.Activity.objects.filter(id__in=activity_ids))

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


class ProjectLocationView(AbstractProjectView):
    template_name = "projects/location.html"
    breadcrumbs = (("Home", reverse_lazy("home")), ("Project description", ""))

    def post(self, *args, **kwargs):
        governance = self.request.POST["governance"]
        project_name = self.request.POST["project_name"]
        location_sign = signing.dumps(
            dict(governance=governance, project_name=project_name)
        )
        return HttpResponseRedirect(
            reverse("project-activity", kwargs=dict(location_sign=location_sign))
        )


class ProjectActivityView(AbstractProjectView):
    template_name = "projects/activity.html"

    def get_breadcrumbs(self):
        return (
            ("Home", reverse_lazy("home")),
            ("Project description", reverse("project-location")),
            ("Project activities", ""),
        )

    def post(self, *args, **kwargs):
        activity_ids = [int(i) for i in self.request.POST.getlist("activities")]
        activities = models.Activity.objects.filter(id__in=activity_ids)
        if activities.count() < len(activities):
            raise Http404("Unable to find all the activities")
        activity_sign = signing.dumps(dict(activities=activity_ids))
        return HttpResponseRedirect(
            reverse(
                "project-result",
                kwargs=dict(
                    location_sign=self.kwargs["location_sign"],
                    activity_sign=activity_sign,
                ),
            )
        )


class ProjectResultView(AbstractProjectView):
    template_name = "projects/result.html"
    page_width = "col-md-12"

    def get_breadcrumbs(self):
        return (
            ("Home", reverse_lazy("home")),
            ("Project description", reverse("project-location")),
            (
                "Project activity",
                reverse(
                    "project-activity",
                    kwargs=dict(location_sign=self.kwargs["location_sign"]),
                ),
            ),
            ("Project results", ""),
        )

    def get_org_permissions(self):
        """
        Returns a dictionary of org_type:
        to a set of activities it can do
        """
        org_types = models.OrgType.objects.all()
        result = {}
        for org_type in org_types:
            result[org_type] = org_type.get_activities()

        return result

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["org_permissions"] = self.get_org_permissions()
        return ctx
