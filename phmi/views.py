from collections import OrderedDict
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.contrib.auth import login, logout
from django.db.models.functions import Lower
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from phmi.forms import CareSystemForm, LoginForm, OrganisationForm
from phmi.models import CareSystem, Organisation, OrgType, User


def get_orgs_by_type():
    """
    Generator of OrgType.name, list of Orgs

    Used to build the Organisation filter part of the CareSystem form page.
    """
    for org_type in OrgType.objects.prefetch_related("orgs"):
        yield org_type.name, [
            o for o in org_type.orgs.order_by("name")
        ]


class IsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class GroupAdd(IsStaffMixin, CreateView):
    form_class = CareSystemForm
    model = CareSystem
    template_name = "group_form.html"

    def form_valid(self, form):
        # create the CareSystem
        care_system = CareSystem.objects.create(
            name=form.cleaned_data["name"], type=form.cleaned_data["type"]
        )

        # link the selected orgs to the new caresystem
        care_system.orgs.add(*form.cleaned_data["organisations"])

        return redirect(care_system.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orgs_by_type"] = get_orgs_by_type()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = Organisation.objects.all()
        return kwargs


class GroupDetail(DetailView):
    model = CareSystem
    template_name = "group_detail.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        # lets not use default dict just to stop
        # the weird behaviour of default dicts
        # in django templates
        orgs_by_type = {}
        for organisation in ctx["object"].orgs.all():
            if organisation.type.name not in orgs_by_type:
                orgs_by_type[organisation.type.name] = []
            orgs_by_type[organisation.type.name].append(
                organisation
            )

        # resort keys alphabetically
        ctx["orgs_by_type"] = OrderedDict()
        alphabetical_org_types = sorted(orgs_by_type.keys())
        for alphabetical_org_type in alphabetical_org_types:
            ctx["orgs_by_type"][alphabetical_org_type] = orgs_by_type[
                alphabetical_org_type
            ]
        return ctx


class GroupEdit(IsStaffMixin, UpdateView):
    form_class = CareSystemForm
    model = CareSystem
    template_name = "group_form.html"

    def form_valid(self, form):
        self.object = form.save()

        # link the selected orgs to the caresystem
        self.object.orgs.set(form.cleaned_data["organisations"], clear=True)

        return redirect(self.object.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orgs_by_type"] = get_orgs_by_type()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = Organisation.objects.all()
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["organisations"] = self.object.orgs.all()
        return initial

    def get_object(self, queryset=None):
        qs = self.model.objects.prefetch_related("orgs")
        return super().get_object(queryset=qs)


class OrganisationAdd(IsStaffMixin, CreateView):
    form_class = OrganisationForm
    model = Organisation
    template_name = "organisation_form.html"
    success_url = reverse_lazy("group-add")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type = OrgType.objects.get(name="Other")
        self.object.save()
        return super().form_valid(form)


class Home(ListView):
    model = CareSystem
    template_name = "home.html"


class Logout(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        url = reverse("home")
        return redirect(url)


class Login(View):
    def get(self, request, *args, **kwargs):
        pk = User.get_pk_from_signed_url(kwargs["signed_pk"])

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
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
        user, _ = User.objects.get_or_create(email=form.cleaned_data["email"])

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
