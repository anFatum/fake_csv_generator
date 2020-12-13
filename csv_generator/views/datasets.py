from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, View

from csv_generator.models import Schema, Dataset

User = get_user_model()


class ListDatasetsView(LoginRequiredMixin, ListView):
    model = Dataset
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/datasets/list_datasets.html"
    context_object_name = "datasets"

    def get_queryset(self):
        schema_pk = self.kwargs['pk']
        schema = Schema.objects.filter(pk=schema_pk).first()
        if schema is None or schema.owner != self.request.user:
            raise Http404
        queryset = Dataset.objects.filter(schema=schema)
        return queryset

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["schema_pk"] = self.kwargs['pk']
        return ctx


class GenerateDatasetView(LoginRequiredMixin, View):
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        pass
