from django.core import signing
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from phmi import models
from phmi.views import AbstractPhmiView, BreadcrumbsMixin


class AbstractActivityView(AbstractPhmiView, TemplateView):
    def decode_activity_sign(self):
        if "activity_sign" not in self.kwargs:
            return {}
        activity_ids = signing.loads(self.kwargs["activity_sign"])["activities"]
        return dict(activities=models.Activity.objects.filter(id__in=activity_ids))

    # @cached_property
    # def activities(self):
    #     return

    @cached_property
    def care_systems(self):
        return models.CareSystem.objects.all()

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update(self.decode_activity_sign())
        self.activities = models.Activity.objects.all()
        return ctx


class ActivityAssessmentView(BreadcrumbsMixin, AbstractActivityView):
    breadcrumbs = [
        ("Home", reverse_lazy("home")),
        ("Project activities", ""),
    ]
    template_name = "activity_assessment/activity.html"

    def post(self, *args, **kwargs):
        activity_ids = [int(i) for i in self.request.POST.getlist("activities")]
        activities = models.Activity.objects.filter(id__in=activity_ids)
        if activities.count() < len(activities):
            raise Http404("Unable to find all the activities")
        activity_sign = signing.dumps(dict(activities=activity_ids))
        return HttpResponseRedirect(
            reverse(
                "activity-assessment-result",
                kwargs=dict(
                    activity_sign=activity_sign,
                ),
            )
        )


class ActivityResultView(BreadcrumbsMixin, AbstractActivityView):
    template_name = "activity_assessment/result.html"
    page_width = "col-md-12"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Activity choices", reverse_lazy("activity-assessment")),
            ("Activity results", ""),
        ]

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
