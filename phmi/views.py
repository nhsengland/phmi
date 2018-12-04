from collections import OrderedDict
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.contrib.auth import login, logout
from django.db.models.functions import Lower
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import is_safe_url
from django.views.generic import (
    TemplateView,
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from phmi.forms import CareSystemForm, LoginForm, OrganisationForm
from phmi import models


def get_orgs_by_type():
    """
    Generator of OrgType.name, list of Orgs

    Used to build the Organisation filter part of the CareSystem form page.
    """
    for org_type in models.OrgType.objects.prefetch_related("orgs"):
        yield org_type.name, [
            o for o in org_type.orgs.order_by("name")
        ]


class IsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class AbstractPhmiView(object):
    page_width = "col-md-8"

    def get_breadcrumbs(self):
        return getattr(self, "breadcrumbs", [])


class GroupChangeMixin(object):
    page_width = "col-md-12"

    def get_success_url(self):
        # add_org is added by the submit button to add a new
        # organisation, ie when an organisation is not found
        if "add_org" in self.request.POST:
            url = reverse("organisation-add")
            return "{}?name={}&care_system={}".format(
                url, self.request.POST["search_term"], self.object.id
            )
        else:
            return super().get_success_url()


class GroupAdd(IsStaffMixin, GroupChangeMixin, AbstractPhmiView, CreateView):
    form_class = CareSystemForm
    model = models.CareSystem
    template_name = "group_form.html"

    def get_breadcrumbs(self):
        return (
            ("Home", "/"),
            ("Care systems", reverse("group-list")),
            ("Add", "")
        )

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


class GroupDetail(AbstractPhmiView, DetailView):
    model = models.CareSystem
    template_name = "group_detail.html"

    def get_breadcrumbs(self):
        return (
            ("Home", "/"),
            ("Care systems", reverse("group-list")),
            (self.object.name, "")
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        # lets not use default dict just to stop
        # the weird behaviour of default dicts
        # in django templates
        orgs_by_type = {}
        for organisation in ctx["object"].orgs.all():
            if organisation.type not in orgs_by_type:
                orgs_by_type[organisation.type] = []
            orgs_by_type[organisation.type].append(
                organisation
            )

        # resort keys alphabetically
        ctx["orgs_by_type"] = OrderedDict()
        alphabetical_org_types = sorted(
            orgs_by_type.keys(), key=lambda x: x.name
        )
        for alphabetical_org_type in alphabetical_org_types:
            ctx["orgs_by_type"][alphabetical_org_type] = orgs_by_type[
                alphabetical_org_type
            ]

        return ctx


class GroupEdit(IsStaffMixin, GroupChangeMixin, AbstractPhmiView, UpdateView):
    form_class = CareSystemForm
    model = models.CareSystem
    template_name = "group_form.html"

    def get_breadcrumbs(self):
        return (
            ("Home", "/"),
            ("Care systems", reverse("group-list")),
            (self.object.name, self.object.get_absolute_url()),
            ("Edit", "")
        )

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


class OrgTypeList(AbstractPhmiView, ListView):
    model = models.OrgType
    template_name = "orgtype_list.html"

    breadcrumbs = (
        ("Home", "/"),
        ("Organizations", "")
    )


class OrgTypeDetail(AbstractPhmiView, DetailView):
    model = models.OrgType
    template_name = "orgtype_detail.html"
    page_width = "col-md-12"

    def get_breadcrumbs(self):
        return (
            ("Home", "/",),
            ("Organizations", reverse("org-type-list")),
            (
                self.object.name, ""
            )
        )

    def get_activities(self):
        """
            returns an ordered dictionary of
            {
                actvity_name: allowed=True
                              allowed_orgs=[]
                              [legal_justifications]
            }
        """
        org_type_activities_ids = set(self.object.get_activities().values_list(
            "id", flat=True
        ))
        result = OrderedDict()
        for i in models.Activity.objects.all():
            allowed = i.id in org_type_activities_ids
            justifications = []
            if allowed:
                justifications = i.legaljustification_set.filter(
                    org_type=self.object
                ).values_list("name", flat=True).distinct()

            result[i] = dict(
                allowed=allowed,
                justifications=justifications,
            )
        return result


class ActivityList(AbstractPhmiView, ListView):
    model = models.Activity
    template_name = "activity_list.html"
    page_width = "col-md-12"

    breadcrumbs = (
        ("Home", "/"),
        ("Activities", "")
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


class ActivityDetail(AbstractPhmiView, DetailView):
    model = models.Activity
    template_name = "activity_detail.html"
    page_width = "col-md-12"

    def get_breadcrumbs(self):
        return (
            ("Home", "/"),
            ("Activities", reverse("activity-list")),
            (self.object.name, self.object.get_absolute_url())
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        data = []
        for orgtype in self.object.get_org_types():
            data.append(
                dict(
                    name=orgtype.name,
                    slug=orgtype.slug,
                    justifications=models.LegalJustification.objects.filter(
                        org_type=orgtype
                    ).filter(activities=self.object)
                )
            )

        ctx["org_types"] = data
        return ctx


class OrganisationAdd(AbstractPhmiView, IsStaffMixin, CreateView):
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
        care_system = models.CareSystem.objects.get(
            id=self.request.GET["care_system"]
        )
        self.object.care_system.add(care_system)
        return super().form_valid(form)


class GroupList(AbstractPhmiView, ListView):
    breadcrumbs = (
        ("Home", "/"),
        ("Care systems", "")
    )
    model = models.CareSystem
    template_name = "group_list.html"


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        url = reverse("home")
        return redirect(url)


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

        url = user.care_system.get_absolute_url() if user.care_system else "/"
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
                self.request,
                "A login URL has been sent tor your email address"
            )
        else:
            msg = [
                "<div class='text-center'>",
                "In production an email would have been sent to you,",
                "for devlopment purposes, login by clicking <a href='{}'>here</a>",
                "</div>"
            ]
            messages.success(
                self.request,
                mark_safe(" ".join(msg).format(absolute_url))
            )

        return redirect(reverse("request-login"))
