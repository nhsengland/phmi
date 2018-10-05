from django.contrib import messages
from django.contrib.auth import login
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from .forms import CareSystemForm, LoginForm
from .models import CareSystem, Organisation, OrgType, User


class GroupAdd(CreateView):
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = Organisation.objects.all()
        return kwargs


class GroupDetail(DetailView):
    model = CareSystem
    template_name = "group_detail.html"


class GroupEdit(UpdateView):
    form_class = CareSystemForm
    model = CareSystem
    template_name = "group_form.html"

    def form_valid(self, form):
        self.object = form.save()

        # link the selected orgs to the caresystem
        self.object.orgs.set(form.cleaned_data["organisations"], clear=True)

        return redirect(self.object.get_absolute_url())

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


class Home(ListView):
    model = CareSystem
    template_name = "home.html"

    def get_queryset(self):
        return super().get_queryset().order_by(Lower("name"))


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

        url = reverse("login", kwargs={"signed_pk": user.sign_pk()})
        absolute_url = self.request.build_absolute_uri(url)
        user.email_login_url(absolute_url)

        messages.success(
            self.request, "A login URL has been sent tor your email address"
        )

        return redirect(reverse("request-login"))


class OrganisationList(View):
    def get(self, request, *args, **kwargs):
        data = {"results": []}
        for org_type in OrgType.objects.prefetch_related("orgs"):
            data["results"].append(
                {
                    "text": org_type.name,
                    "children": [
                        {"id": o.id, "text": o.name}
                        for o in org_type.orgs.order_by("name")
                    ],
                }
            )

        return JsonResponse(data)
