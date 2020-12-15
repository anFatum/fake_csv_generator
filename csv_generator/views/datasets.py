from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, View
from csv_generator.tasks import generate_dataset
from csv_generator.models import Schema, Dataset
from django.shortcuts import redirect, reverse
from celery import current_app
from django.http.response import JsonResponse

User = get_user_model()


class ListDatasetsView(LoginRequiredMixin, ListView):
    """
    List all datasets that are connected to schema
    """
    model = Dataset
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'
    template_name = "csv_generator/datasets/list_datasets.html"
    context_object_name = "datasets"

    def get_queryset(self):
        schema_pk = self.kwargs['pk']
        schema = Schema.objects.filter(pk=schema_pk).first()
        # if user is not the schema owner request is not allowed
        if schema is None or schema.owner != self.request.user:
            raise Http404
        queryset = Dataset.objects.filter(schema=schema).order_by("created")
        return queryset

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["schema_pk"] = self.kwargs['pk']
        ctx["errors"] = self.request.GET.get("errors")
        return ctx


class GenerateDatasetView(LoginRequiredMixin, View):
    """
    View to generate dataset. Runs celery background task
    """
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'

    def post(self, request, *args, **kwargs):
        """
        POST request to generate new dataset with user provided
        row counts. If row count < 1 give user error info this number
        should be more than 0
        :param request: HTTP request
        :type request:
        :return: HTTP response
        :rtype:
        """
        row_count = request.POST.get('rows_number', None)
        if row_count is None or int(row_count) < 0:
            response = redirect(reverse("csv:list-dataset", kwargs=self.kwargs))
            response['Location'] += '?errors=Wrong row count'
            return response
        new_dataset = Dataset(
            schema_id=self.kwargs['pk'],
            rows=int(row_count)
        )
        new_dataset.save()
        # Run celery background task
        task = generate_dataset.delay(new_dataset.pk)
        new_dataset.task_id = task.id
        new_dataset.save()
        return redirect(reverse("csv:list-dataset", kwargs=self.kwargs))


class GetDatasetStatus(LoginRequiredMixin, View):
    """
    View to get task result
    """
    login_url = "/auth/login"
    redirect_field_name = 'redirect_to'

    def get(self, request, task_id):
        """
        Asks celery the task status and returns it to the user
        :param request: HTTP request
        :type request:
        :param task_id: task id user asks server about
        :type task_id:
        :return: HTTP response
        :rtype:
        """
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id,
                         'url': task.result}
        dataset = Dataset.objects.get(task_id=task_id)
        dataset.task_status = response_data['task_status']
        dataset.save()
        return JsonResponse(response_data)
