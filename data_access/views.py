from django.core import signing
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from phmi.models import Activity, ActivityCategory, DataType, OrgType, Service
from phmi.views import BreadcrumbsMixin

from .forms import ActivitiesForm, ActivityCategoryForm, OrgTypesForm, ServicesForm


class SignedDataMixin:
    def dispatch(self, request, *args, **kwargs):
        """Get the current data from the signed JSON payload in the current URL."""
        try:
            self.current_data = signing.loads(self.kwargs["signed_data"])
        except KeyError:
            self.current_data = {}

        return super().dispatch(request, *args, **kwargs)

    def next_page(self, extra_data):
        """Build up a dictionary of data to dump into the URL"""
        data = dict(self.current_data)  # use dict constructor to avoid pass by ref
        data.update(extra_data)  # merge in specific view data

        signed_data = signing.dumps(data)

        return redirect(
            reverse(
                f"data_access:{self.next_page_url_name}",
                kwargs={"signed_data": signed_data},
            )
        )


class ActivitiesView(SignedDataMixin, BreadcrumbsMixin, FormView):
    breadcrumbs = [
        ("Home", reverse_lazy("home")),
        # ("Categories", reverse_lazy("data-access:categories")),
        ("Activities", ""),
    ]
    form_class = ActivitiesForm
    next_page_url_name = "org-types"
    template_name = "data_access/activities.html"

    def form_valid(self, form):
        data = {"activity_id": form.cleaned_data["activities"].id}
        return self.next_page(data)

    def get_form_kwargs(self):
        category_id = self.current_data["category_id"]
        activities = Activity.objects.filter(activity_category_id=category_id).order_by(
            "name"
        )

        kwargs = super().get_form_kwargs()
        kwargs["activities"] = activities
        return kwargs


class ActivityCategoryView(SignedDataMixin, BreadcrumbsMixin, FormView):
    breadcrumbs = [("Home", reverse_lazy("home")), ("Categories", "")]
    form_class = ActivityCategoryForm
    next_page_url_name = "activities"
    template_name = "data_access/categories.html"

    def form_valid(self, form):
        data = {"category_id": form.cleaned_data["categories"].id}
        return self.next_page(data)

    def get_form_kwargs(self):
        categories = ActivityCategory.objects.order_by("name")

        kwargs = super().get_form_kwargs()
        kwargs["categories"] = categories
        return kwargs


class OrgTypesView(SignedDataMixin, BreadcrumbsMixin, FormView):
    breadcrumbs = [
        ("Home", reverse_lazy("home")),
        # ("Categories", reverse_lazy("data-access:categories")),
        # ("Activities", reverse_lazy("data-access:activities")),
        ("Organisation Types", ""),
    ]
    form_class = OrgTypesForm
    next_page_url_name = "services"
    template_name = "data_access/org_types.html"

    def form_valid(self, form):
        org_type_ids = list(form.cleaned_data["org_types"].values_list("pk", flat=True))
        data = {"org_type_ids": org_type_ids}
        return self.next_page(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["org_types"] = OrgType.objects.order_by("name")
        return kwargs


class OutcomeView(SignedDataMixin, BreadcrumbsMixin, TemplateView):
    breadcrumbs = [
        ("Home", reverse_lazy("home")),
        # ("Categories", reverse_lazy("data-access:categories")),
        # ("Activities", reverse_lazy("data-access:activities")),
        # ("Organisation Types", reverse_lazy("data-access:org-types")),
        # ("Services", reverse_lazy("data-access:services")),
        ("Outcome", ""),
    ]
    template_name = "data_access/outcome.html"

    def get_context_data(self, **kwargs):
        activity = Activity.objects.get(pk=self.current_data["activity_id"])
        category = ActivityCategory.objects.get(pk=self.current_data["category_id"])
        org_types = OrgType.objects.filter(pk__in=self.current_data["org_type_ids"])
        services = Service.objects.filter(pk__in=self.current_data["service_ids"])

        # Get a list of DataType IDs which should have a tick
        allowed_data_type_ids = set(
            DataType.objects.filter(
                activities=activity, org_types__in=org_types, services__in=services
            ).values_list("pk", flat=True)
        )

        # Get a full list of DataTypes
        data_types = DataType.objects.select_related("category").order_by(
            "category__name", "name"
        )

        context = super().get_context_data(**kwargs)
        context["allowed_data_type_ids"] = allowed_data_type_ids
        context["data_types"] = data_types
        context["selected_activity"] = activity
        context["selected_category"] = category
        context["selected_org_types"] = org_types
        context["selected_services"] = services
        return context


class ServicesView(SignedDataMixin, BreadcrumbsMixin, FormView):
    breadcrumbs = [
        ("Home", reverse_lazy("home")),
        # ("Categories", reverse_lazy("data-access:categories")),
        # ("Activities", reverse_lazy("data-access:activities")),
        # ("Organisation Types", reverse_lazy("data-access:org-types")),
        ("Services", ""),
    ]
    form_class = ServicesForm
    next_page_url_name = "outcome"
    template_name = "data_access/services.html"

    def form_valid(self, form):
        service_ids = list(form.cleaned_data["services"].values_list("pk", flat=True))
        data = {"service_ids": service_ids}
        return self.next_page(data)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["services"] = Service.objects.order_by("name")
        return kwargs
