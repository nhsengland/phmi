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


class GroupEdit(UpdateView):
    form_class = CareSystemForm
    model = CareSystem
    template_name = "group_edit.html"

    def form_valid(self, form):
        self.object = form.save()

        # link the selected orgs to the caresystem
        self.object.orgs.add(*form.cleaned_data["organisations"])

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
