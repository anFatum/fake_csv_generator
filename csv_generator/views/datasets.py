from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, View
from csv_generator.tasks import generate_dataset
from csv_generator.models import Schema, Dataset
from django.shortcuts import render, redirect, reverse
from celery import current_app
from django.http.response import JsonResponse

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
        row_count = int(request.POST.get('rows_number', None))
        if row_count is None or row_count < 0:
            raise Http404
        new_dataset = Dataset(
            schema_id=self.kwargs['pk'],
            rows=row_count
        )
        new_dataset.save()
        task = generate_dataset.delay(new_dataset.pk)
        new_dataset.task_id = task.id
        new_dataset.save()
        return redirect(reverse("csv:list-dataset", kwargs=self.kwargs))


class GetDatasetStatus(LoginRequiredMixin, View):
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'

    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}
        dataset = Dataset.objects.get(task_id=task_id)
        dataset.task_status = response_data['task_status']
        dataset.save()
        return JsonResponse(response_data)
