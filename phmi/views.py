from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from . import models
from .forms import (
    CareSystemForm,
    DataAccessForm,
    DataTypeSelectorForm,
    LoginForm,
    OrganisationForm,
)


def get_orgs_by_type():
    """
    Generator of OrgType.name, list of Orgs

    Used to build the Organisation filter part of the CareSystem form page.
    """
    for org_type in models.OrgType.objects.prefetch_related("orgs"):
        yield org_type.name, [o for o in org_type.orgs.order_by("name")]


class IsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class AbstractPhmiView(object):
    page_width = "col-md-8"


class BreadcrumbsMixin:
    """
    Mixin to add breadcrumbs support to a subclass

    When inheriting from this Mixin one can add a list of tuples containing a
    label and URL string, for example:

        breadcrumbs = [
            ("Home", reverse_lazy("home"))
            ("Intermediate Page", reverse_lazy("intermediate"))
            ("Current Page", "")
        ]

    """

    breadcrumbs = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = self.breadcrumbs
        return context


class GroupChangeMixin(object):
    page_width = "col-md-12"

    def get_success_url(self):
        # add_org is added by the submit button to add a new
        # organisation, ie when an organisation is not found
        if "add_org" not in self.request.POST:
            return super().get_success_url()

        url = reverse("organisation-add")
        search_term = self.request.POST["search_term"]
        return f"{url}?name={search_term}&care_system={self.object.id}"


class GroupAdd(
    IsStaffMixin, GroupChangeMixin, BreadcrumbsMixin, AbstractPhmiView, CreateView
):
    breadcrumbs = [
        ("Home", reverse_lazy("home")),
        ("Care systems", reverse_lazy("group-list")),
        ("Add", ""),
    ]
    form_class = CareSystemForm
    model = models.CareSystem
    template_name = "group_form.html"

    def form_valid(self, form):
        # create the CareSystem
        result = super().form_valid(form)
        self.object.orgs.add(*form.cleaned_data["organisations"])
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orgs_by_type"] = get_orgs_by_type()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = models.Organisation.objects.all()
        return kwargs


class Home(AbstractPhmiView, ListView):
    model = models.ActivityCategory
    template_name = "home.html"
    page_width = "col-md-12"
    queryset = models.ActivityCategory.objects.exclude(group=None)


class GroupDetail(AbstractPhmiView, DetailView):
    model = models.CareSystem
    template_name = "group_detail.html"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Care systems", reverse("group-list")),
            (self.object.name, ""),
        ]

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        # lets not use default dict just to stop
        # the weird behaviour of default dicts
        # in django templates
        orgs_by_type = {}
        for organisation in ctx["object"].orgs.all():
            if organisation.type not in orgs_by_type:
                orgs_by_type[organisation.type] = []
            orgs_by_type[organisation.type].append(organisation)

        # resort keys alphabetically
        ctx["orgs_by_type"] = OrderedDict()
        alphabetical_org_types = sorted(orgs_by_type.keys(), key=lambda x: x.name)
        for alphabetical_org_type in alphabetical_org_types:
            ctx["orgs_by_type"][alphabetical_org_type] = orgs_by_type[
                alphabetical_org_type
            ]

        return ctx


class GroupEdit(
    IsStaffMixin, GroupChangeMixin, BreadcrumbsMixin, AbstractPhmiView, UpdateView
):
    form_class = CareSystemForm
    model = models.CareSystem
    template_name = "group_form.html"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Care systems", reverse("group-list")),
            (self.object.name, self.object.get_absolute_url()),
            ("Edit", ""),
        ]

    def form_valid(self, form):
        # create the CareSystem
        result = super().form_valid(form)

        # link the selected orgs to the caresystem
        self.object.orgs.set(form.cleaned_data["organisations"], clear=True)

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orgs_by_type"] = get_orgs_by_type()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = models.Organisation.objects.all()
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["organisations"] = self.object.orgs.all()
        return initial

    def get_object(self, queryset=None):
        qs = self.model.objects.prefetch_related("orgs")
        return super().get_object(queryset=qs)


class OrgTypeList(BreadcrumbsMixin, AbstractPhmiView, ListView):
    breadcrumbs = [("Home", reverse_lazy("home")), ("Organizations", "")]
    model = models.OrgType
    template_name = "orgtype_list.html"


class OrgTypeDetail(BreadcrumbsMixin, AbstractPhmiView, DetailView):
    model = models.OrgType
    template_name = "orgtype_detail.html"
    page_width = "col-md-12"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Organizations", reverse("org-type-list")),
            (self.object.name, ""),
        ]

    def get_activities(self, org_type):
        """
        Get the activities for the given OrgType

        Returns an ordered dictionary:

            {
                Actvity: {
                    "allowed": True,
                    "justifications": [legal_justifications],
                },
            }
        """
        org_type_activities_ids = set(
            org_type.get_activities().values_list("id", flat=True)
        )

        for activity in models.Activity.objects.all():
            allowed = activity.id in org_type_activities_ids
            justifications = []

            if allowed:
                justifications = (
                    activity.legal_justifications.filter(org_type=org_type)
                    .values_list("name", flat=True)
                    .distinct()
                )

            yield activity, {"allowed": allowed, "justifications": justifications}

    def get_context_data(self, **kwargs):
        activity_category_groups = models.ActivityCategoryGroup.objects.prefetch_related(
            "categories", "categories__activities"
        )

        context = super().get_context_data(**kwargs)
        context["allowed_activities"] = self.object.get_activities()
        context["activity_category_groups"] = activity_category_groups
        return context


class ActivityList(BreadcrumbsMixin, AbstractPhmiView, ListView):
    breadcrumbs = [("Home", reverse_lazy("home")), ("Activities", "")]
    template_name = "activity_list.html"
    page_width = "col-md-12"
    queryset = models.ActivityCategoryGroup.objects.prefetch_related(
        "categories", "categories__activities"
    )

    def get_context_data(self, *args, **kwargs):
        # We are skipping "Local Authority (Public Health)" and just doing
        # "Local Authority (Non-Public Health)" currently.
        org_types = models.OrgType.objects.exclude(
            name="Local Authority (Public Health)"
        )
        org_permissions = {
            org_type: org_type.get_activities() for org_type in org_types
        }

        ctx = super().get_context_data(*args, **kwargs)
        ctx["org_permissions"] = org_permissions
        return ctx


class ActivityDetail(BreadcrumbsMixin, AbstractPhmiView, DetailView):
    model = models.Activity
    template_name = "activity_detail.html"
    page_width = "col-md-12"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Activities", reverse("activity-list")),
            (self.object.name, self.object.get_absolute_url()),
        ]

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        data = []
        for org_type in self.object.get_org_types():
            justifications = org_type.legal_justifications.filter(activity=self.object)
            lawful_bases = models.LawfulBasis.objects.filter(
                legal_justifications__in=justifications
            )

            data.append(
                {
                    "name": org_type.name,
                    "slug": org_type.slug,
                    "url": org_type.get_absolute_url,
                    "lawful_bases": lawful_bases,
                }
            )

        ctx["org_types"] = data
        return ctx


class OrganisationAdd(BreadcrumbsMixin, AbstractPhmiView, IsStaffMixin, CreateView):
    form_class = OrganisationForm
    model = models.Organisation
    template_name = "organisation_form.html"

    def get_success_url(self, *args, **kwargs):
        care_system = self.request.GET["care_system"]
        return reverse("group-edit", kwargs=dict(pk=care_system))

    def get_initial(self):
        initial = super().get_initial()
        if "name" in self.request.GET:
            initial["name"] = self.request.GET["name"]
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type = models.OrgType.objects.get(name="Other")
        self.object.save()
        care_system = models.CareSystem.objects.get(id=self.request.GET["care_system"])
        self.object.care_system.add(care_system)
        return super().form_valid(form)


class GroupList(BreadcrumbsMixin, AbstractPhmiView, ListView):
    breadcrumbs = [("Home", reverse_lazy("home")), ("Care systems", "")]
    model = models.CareSystem
    template_name = "group_list.html"


class Login(View):
    def get(self, request, *args, **kwargs):
        pk = models.User.get_pk_from_signed_url(kwargs["signed_pk"])

        try:
            user = models.User.objects.get(pk=pk)
        except models.User.DoesNotExist:
            messages.error(request, "Unknown user, please login")
            return redirect(reverse("login"))

        # manually set the User's backend since Django's ModelBackend requires
        # a password and we aren't setting those on our custom User model.
        login(request, user)

        url = (
            user.care_system.get_absolute_url()
            if user.care_system
            else reverse_lazy("home")
        )
        return redirect(url)


class GenerateMagicLoginURL(FormView):
    form_class = LoginForm
    template_name = "login.html"

    def form_valid(self, form):
        """Email a login URL to the address specified by the user."""
        user, _ = models.User.objects.get_or_create(email=form.cleaned_data["email"])

        # if the user's email ends in one of the STAFF_LOGIN_DOMAINS
        # automatically set is_staff to be True
        if not user.is_staff:
            if user.email.endswith(tuple(settings.STAFF_LOGIN_DOMAINS)):
                user.is_staff = True
                user.save()

        url = reverse("login", kwargs={"signed_pk": user.sign_pk()})
        absolute_url = self.request.build_absolute_uri(url)

        if settings.EMAIL_LOGIN:
            user.email_login_url(absolute_url)
            messages.success(
                self.request, "A login URL has been sent tor your email address"
            )
        else:
            msg = [
                "<div class='text-center'>",
                "In production an email would have been sent to you,",
                "for devlopment purposes, login by clicking <a href='{}'>here</a>",
                "</div>",
            ]
            messages.success(
                self.request, mark_safe(" ".join(msg).format(absolute_url))
            )

        return redirect(reverse("request-login"))


class DataAccessView(BreadcrumbsMixin, TemplateView):
    breadcrumbs = [("Home", reverse_lazy("home")), ("Data access", "")]
    page_width = "col-md-12"
    template_name = "data_access.html"

    def get_context_data(self, **kwargs):
        all_org_types = models.OrgType.objects.all()
        all_services = models.Service.objects.all()

        # Get objects from Query Args
        selected_activity = models.Activity.objects.filter(
            pk=self.request.GET.get("activities")
        ).first()

        # default to all org types if none are selected
        selected_org_types = all_org_types.all()
        selected_org_type_ids = self.request.GET.getlist("org_types")
        if selected_org_type_ids:
            selected_org_types = all_org_types.filter(pk__in=selected_org_type_ids)

        # default to all services if none are selected
        selected_services = all_services.all()
        selected_service_ids = self.request.GET.getlist("services")
        if selected_service_ids:
            selected_services = all_services.filter(pk__in=selected_service_ids)

        # Get a list of DataType IDs which should have a tick
        allowed_data_type_ids = set(
            models.DataType.objects.filter(
                activities=selected_activity,
                org_types__in=selected_org_types,
                services__in=selected_services,
            ).values_list("pk", flat=True)
        )

        # Get a full list of DataTypes
        data_types = models.DataType.objects.select_related("category").order_by(
            "category__name", "name"
        )

        # Build the form
        form = DataAccessForm(
            models.Activity.objects.select_related("activity_category").order_by(
                "activity_category__index", "name"
            ),
            all_org_types.order_by("name"),
            all_services.order_by("name"),
        )

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "allowed_data_type_ids": allowed_data_type_ids,
                "data_types": data_types,
                "form": form,
                "selected_activity": selected_activity,
                "selected_org_types": selected_org_types,
                "selected_services": selected_services,
            }
        )
        return context


class DataTypeSelector(BreadcrumbsMixin, FormView):
    breadcrumbs = [("Home", reverse_lazy("home")), ("Data access selector", "")]
    form_class = DataTypeSelectorForm
    page_width = "col-md-12"
    template_name = "data_type_selector.html"

    def form_valid(self, form):
        data_type = form.cleaned_data["data_type"]
        url = reverse("data-type-results", kwargs={"pk": data_type.pk})
        return redirect(url)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["data_types"] = models.DataType.objects.order_by("name")
        return kwargs


class DataTypeResults(BreadcrumbsMixin, TemplateView):
    page_width = "col-md-12"
    template_name = "data_type_results.html"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Data access selector", reverse_lazy("data-type-selector")),
            (self.data_type.name, ""),
        ]

    def get(self, request, *args, **kwargs):
        try:
            self.data_type = models.DataType.objects.get(pk=self.kwargs["pk"])
        except models.DataType.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["data_type"] = self.data_type
        return context


class DataTypeOrgTypeLegalJustifications(BreadcrumbsMixin, TemplateView):
    page_width = "col-md-12"
    template_name = "data_type_org_type.html"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Data access selector", reverse_lazy("data-type-selector")),
            (
                self.data_type.name,
                reverse_lazy("data-type-results", kwargs={"pk": self.kwargs["pk"]}),
            ),
            (self.org_type.name, ""),
        ]

    def get(self, request, *args, **kwargs):
        try:
            self.data_type = models.DataType.objects.get(pk=self.kwargs["pk"])
        except models.DataType.DoesNotExist:
            raise Http404

        try:
            self.org_type = models.OrgType.objects.get(
                pk=self.kwargs["org_type_pk"], data_types=self.data_type
            )
        except models.OrgType.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["org_type"] = self.org_type
        return context


class DataTypeActivityLegalJustifications(BreadcrumbsMixin, TemplateView):
    page_width = "col-md-12"
    template_name = "data_type_activity.html"

    @property
    def breadcrumbs(self):
        return [
            ("Home", reverse_lazy("home")),
            ("Data access selector", reverse_lazy("data-type-selector")),
            (
                self.data_type.name,
                reverse_lazy("data-type-results", kwargs={"pk": self.kwargs["pk"]}),
            ),
            (self.activity.name, ""),
        ]

    def get(self, request, *args, **kwargs):
        try:
            self.data_type = models.DataType.objects.get(pk=self.kwargs["pk"])
        except models.DataType.DoesNotExist:
            raise Http404

        try:
            self.activity = models.Activity.objects.get(
                pk=self.kwargs["activity_pk"], data_types=self.data_type
            )
        except models.Activity.DoesNotExist:
            raise Http404

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activity"] = self.activity
        return context
