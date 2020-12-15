from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from csv_generator.forms import SchemaForm, CreateSchemaInlineFormSet, \
    EditSchemaInlineFormSet
from csv_generator.models import Schema, Field

User = get_user_model()


class OnlySchemaOwnerAllowedMixin:
    """
    Mixin that allows only owners to delete and modify schema
    """
    model = Schema
    lookup = 'pk'

    def get_object(self, queryset=None):
        """
        Only owner should have access to make Update and Delete
         actions
        on schema
        :param queryset:
        :type queryset:
        :return:
        :rtype:
        """
        pk = self.kwargs.get(self.lookup)
        obj = get_object_or_404(self.model, pk=pk) if \
            pk is not None else None
        if obj is None or obj.owner != self.request.user:
            raise Http404
        return obj


class ListSchemasView(LoginRequiredMixin, ListView):
    """
    List all schemas created by user
    """
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/schemas/list_schema.html"
    context_object_name = "schemas"

    def get_queryset(self):
        user = self.request.user
        queryset = Schema.objects.all().order_by("-modified")
        return queryset.filter(owner=user)


class CreateSchemaView(LoginRequiredMixin, CreateView):
    """
    Basic Create view to create schema.
    Only logged users allowed
    """
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
            # if form was marked to be deleted no need to
            # save it
            if inner_form in formset.deleted_forms:
                continue
            field = inner_form.save(commit=False)
            field.schema = new_schema
            # Some fields has optional field options
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
            # if form was marked to be deleted no need to
            # pass it to the template
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
            ctx['inlines'] = self.formset_class()
        return ctx


class DeleteSchemaView(LoginRequiredMixin, OnlySchemaOwnerAllowedMixin,
                       DeleteView):
    """
    Basic delete schema view. Only authorized users who
    own schema are allowed
    """
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy("csv:index")
    context_object_name = "schema"
    template_name = "csv_generator/schemas/delete_schema.html"


class UpdateSchemaView(LoginRequiredMixin, OnlySchemaOwnerAllowedMixin,
                       UpdateView):
    """
    Basic update schema view. Only authorized users who
    own schema are allowed
    """
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    success_url = reverse_lazy("csv:index")
    template_name = "csv_generator/schemas/detailed_schema.html"
    form_class = SchemaForm
    formset_class = EditSchemaInlineFormSet

    def post(self, request, **kwargs):
        """
        POST request to update model
        As Schema has inline formset with fields post
        method handles field forms as well
        :param request: HTTP request
        :type request:
        :return: HTTP response
        :rtype: HttpResponse
        """
        data = request.POST.copy()
        form = self.form_class(data, instance=self.get_object())
        inline_forms = self.formset_class(data, instance=self.get_object())
        if inline_forms.is_valid():
            # Delete fields that marked as deleted
            for f in inline_forms.deleted_forms:
                field = f.save(commit=False)
                field.delete()
            # Save only forms that weren't marked as deleted
            new_forms = [x for x in inline_forms.forms
                         if x not in inline_forms.deleted_forms]
            for f in new_forms:
                field = f.save(commit=False)
                # Some fields get additional options variable
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
