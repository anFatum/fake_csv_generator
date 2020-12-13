from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from csv_generator.forms import SchemaForm
from csv_generator.models import Schema

User = get_user_model()


class ListSchemasView(LoginRequiredMixin, ListView):
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/schemas/list_schema.html"
    context_object_name = "schemas"

    def get_queryset(self):
        user = self.request.user
        queryset = Schema.objects.all()
        if user is not None:
            return queryset.filter(owner=user)
        return queryset


class CreateSchemaView(LoginRequiredMixin, CreateView):
    model = Schema
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/schemas/detailed_schema.html"
    form_class = SchemaForm

    def form_valid(self, form):
        new_schema = form.save(commit=False)
        new_schema.save()
        return redirect(reverse("csv:index"))

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = self.form_class(data)
        form.instance.owner = request.user
        if form.is_valid():
            self.form_valid(form)

        return render(self.request,
                      self.template_name,
                      {"form": form})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['form'] = SchemaForm(self.request.POST)
        else:
            ctx['form'] = SchemaForm()
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

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.owner != self.request.user:
            raise Http404
        return obj
