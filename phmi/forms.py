from django import forms

from .models import CareSystem


class CareSystemForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={"size": "40"}))

    class Meta:
        fields = ["name", "type"]
        model = CareSystem

    def __init__(self, organisations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organisations"] = forms.ModelMultipleChoiceField(
            queryset=organisations
        )
