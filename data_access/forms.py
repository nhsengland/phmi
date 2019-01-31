from django import forms


class ActivitiesForm(forms.Form):
    def __init__(self, activities, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["activities"] = forms.ModelChoiceField(
            queryset=activities, widget=forms.Select(attrs={"class": "form-control"})
        )


class ActivityCategoryForm(forms.Form):
    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["categories"] = forms.ModelChoiceField(
            queryset=categories, widget=forms.Select(attrs={"class": "form-control"})
        )


class OrgTypesForm(forms.Form):
    def __init__(self, org_types, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["org_types"] = forms.ModelMultipleChoiceField(
            label="Organisation Types",
            queryset=org_types,
            widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"}),
        )


class ServicesForm(forms.Form):
    def __init__(self, services, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["services"] = forms.ModelMultipleChoiceField(
            queryset=services,
            widget=forms.CheckboxSelectMultiple(attrs={"class": "form-control"}),
        )
