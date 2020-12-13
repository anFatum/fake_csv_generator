from django import forms
from csv_generator.models import Schema, Character
from django.core.exceptions import ValidationError


class SchemaForm(forms.ModelForm):
    title = forms.CharField(max_length=128, label="Name",
                            widget=forms.TextInput(
                                attrs={"class": "form-control"}
                            ))
    column_separator = forms.ModelChoiceField(
        queryset=Character.objects.column_separators(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    string_character = forms.ModelChoiceField(
        queryset=Character.objects.string_characters(),
        empty_label=None,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Schema
        fields = ("title", "column_separator", "string_character")

    def clean_title(self):
        qs = Schema.objects.filter(owner=self.instance.owner)
        schema = qs.filter(title=self.cleaned_data['title']).first()
        if schema is not None and schema.id != self.instance.id:
            raise ValidationError("User should have unique schema titles")
        return self.cleaned_data['title']

