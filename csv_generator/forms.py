from django import forms
from django.core.exceptions import ValidationError

from csv_generator.models import Schema, Character, Field, FieldType


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


class FieldForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128,
        label="Column name",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    field_type = forms.ChoiceField(
        choices=FieldType.choices,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    order = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Field
        fields = ("name", "field_type", "order")
        exclude = ("id", "schema",)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['field_type'] == FieldType.INTEGER:
            from_range = int(self.data[f"{self.prefix}-from"])
            to_range = int(self.data[f"{self.prefix}-to"])
            cleaned_data["options"] = {
                "from": from_range,
                "to": to_range
            }
        return cleaned_data


class UniqueFieldsFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """Checks that no two fields have the same name."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        fields = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            title = form.cleaned_data.get('name')
            if title in fields:
                raise ValidationError("Titles in a set must have distinct titles.")
            fields.append(title)


CreateSchemaInlineFormSet = forms.inlineformset_factory(
    Schema,
    Field,
    form=FieldForm,
    can_delete=False,
    can_order=False,
    extra=-1,
    min_num=1,
    validate_min=True
)

EditSchemaInlineFormSet = forms.inlineformset_factory(
    Schema,
    Field,
    form=FieldForm,
    can_delete=False,
    can_order=False,
    extra=0,
    min_num=1,
    validate_min=True
)
