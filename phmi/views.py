from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CareSystemForm
from .models import CareSystem, Organisation


class GroupAdd(CreateView):
    form_class = CareSystemForm
    model = CareSystem
    template_name = "group_add.html"

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


class Home(ListView):
    model = CareSystem
    template_name = "home.html"
