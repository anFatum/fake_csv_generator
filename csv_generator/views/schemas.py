from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from csv_generator.forms import SchemaForm, CreateSchemaInlineFormSet, \
    EditSchemaInlineFormSet
from csv_generator.models import Schema, Field

User = get_user_model()


class ListSchemasView(LoginRequiredMixin, ListView):
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/schemas/list_schema.html"
    context_object_name = "schemas"

    def get_queryset(self):
        user = self.request.user
        queryset = Schema.objects.all().order_by("modified")
        return queryset.filter(owner=user)


class CreateSchemaView(LoginRequiredMixin, CreateView):
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/schemas/detailed_schema.html"
    form_class = SchemaForm
    formset_class = CreateSchemaInlineFormSet

    def form_valid(self, form, formset):
        new_schema = form.save(commit=False)
        new_schema.save()
        formset.instance = new_schema
        for inner_form in formset:
            if inner_form in formset.deleted_forms:
                continue
            field = inner_form.save(commit=False)
            field.schema = new_schema
            if 'options' in inner_form.cleaned_data:
                field.options = inner_form.cleaned_data['options']
            field.save()
        return redirect(reverse("csv:index"))

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = self.form_class(data)
        form.instance.owner = request.user
        inline_forms = self.formset_class(data)
        if form.is_valid() and inline_forms.is_valid():
            return self.form_valid(form, inline_forms)
        for d in inline_forms.forms:
            if d.cleaned_data["DELETE"]:
                inline_forms.forms.remove(d)

        return render(self.request,
                      self.template_name,
                      {"form": form,
                       "inlines": inline_forms})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['form'] = SchemaForm(self.request.POST)
            ctx['inlines'] = self.formset_class(self.request.POST)
        else:
            ctx['form'] = SchemaForm()
            inlines = self.formset_class()
            ctx['inlines'] = inlines
        return ctx


class DeleteSchemaView(LoginRequiredMixin, DeleteView):
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy("csv:index")
    context_object_name = "schema"
    template_name = "csv_generator/schemas/delete_schema.html"

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise Http404
        return obj


class UpdateSchemaView(LoginRequiredMixin, UpdateView):
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy("csv:index")
    template_name = "csv_generator/schemas/detailed_schema.html"
    form_class = SchemaForm
    formset_class = EditSchemaInlineFormSet

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise Http404
        return obj

    def post(self, request, **kwargs):
        data = request.POST.copy()
        form = self.form_class(data, instance=self.get_object())
        inline_forms = self.formset_class(data, instance=self.get_object())
        if inline_forms.is_valid():
            for f in inline_forms.deleted_forms:
                field = f.save(commit=False)
                field.delete()
            new_forms = [x for x in inline_forms.forms if x not in inline_forms.deleted_forms]
            for f in new_forms:
                field = f.save(commit=False)
                if 'options' in f.cleaned_data:
                    field.options = f.cleaned_data['options']
                field.save()
            return super().post(request, **kwargs)

        return render(self.request,
                      self.template_name,
                      {"schema": self.get_object(),
                       "form": form,
                       "inlines": inline_forms})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Field.objects.filter(schema=self.object)
        formset = self.formset_class(queryset=qs,
                                     instance=self.object)
        ctx['inlines'] = formset
        return ctx
