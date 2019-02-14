import functools
import itertools
import operator

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from phmi.models import CareSystem, Organisation


class GroupedModelChoiceIterator(forms.models.ModelChoiceIterator):
    """Taken from: https://code.djangoproject.com/ticket/27331#comment:7"""

    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)

        queryset = self.queryset

        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()

        for group, objs in itertools.groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(forms.ModelChoiceField):
    """Taken from: https://code.djangoproject.com/ticket/27331#comment:7"""

    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = operator.attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError(
                "choices_groupby must either be a str or a callable accepting a single argument"
            )

        self.iterator = functools.partial(
            GroupedModelChoiceIterator, groupby=choices_groupby
        )

        super().__init__(*args, **kwargs)


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


class DataAccessForm(forms.Form):
    def __init__(self, activities, org_types, services, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["activities"] = GroupedModelChoiceField(
            queryset=activities,
            choices_groupby=lambda a: a.activity_category,
            widget=forms.Select(attrs={"class": "form-control"}),
        )
        self.fields["org_types"] = forms.ModelMultipleChoiceField(
            label="Organisation Types",
            queryset=org_types,
            widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"}),
        )
        self.fields["services"] = forms.ModelMultipleChoiceField(
            queryset=services,
            widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"}),
        )


class DataTypeSelectorForm(forms.Form):
    def __init__(self, data_types, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["data_type"] = forms.ModelChoiceField(
            queryset=data_types, widget=forms.Select(attrs={"class": "form-control"})
        )


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
