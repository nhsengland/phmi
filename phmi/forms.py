from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from phmi.models import CareSystem, Organisation


class CareSystemForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput)

    class Meta:
        fields = ["name", "type"]
        model = CareSystem

    def __init__(self, organisations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organisations"] = forms.MultipleChoiceField(
            choices=[(o.pk, o.pk) for o in organisations], required=False
        )

        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class OrganisationForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"autofocus": True, "class": "form-control", "size": 50}
        )
    )

    class Meta:
        fields = ["name"]
        model = Organisation


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="NHSmail address *",
        widget=forms.EmailInput(
            attrs={"autofocus": True, "class": "form-control", "size": 50}
        ),
    )

    def clean_email(self):
        """Validate the given email address is at a valid domain."""
        email = self.cleaned_data["email"]

        if not email.endswith(tuple(settings.ALLOWED_LOGIN_DOMAINS)):
            raise ValidationError("Please use an email address from a valid domain")

        return email
