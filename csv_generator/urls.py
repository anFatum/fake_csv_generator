from django.urls import path
from csv_generator.views import ListSchemasView, \
    CreateSchemaView, DeleteSchemaView, UpdateSchemaView, ListDatasetsView, \
    GenerateDatasetView, GetDatasetStatus

app_name = "csv"

urlpatterns = [
    path('', ListSchemasView.as_view(), name='index'),
    path('schema/create/', CreateSchemaView.as_view(), name='schema-create'),
    path('schema/<int:pk>/delete', DeleteSchemaView.as_view(), name="schema-delete"),
    path('schema/<int:pk>', UpdateSchemaView.as_view(), name="schema-update"),
    path('schema/<int:pk>/datasets', ListDatasetsView.as_view(), name="list-dataset"),
    path('schema/<int:pk>/generate', GenerateDatasetView.as_view(), name="generate-dataset"),
    path('dataset/<str:task_id>/status', GetDatasetStatus.as_view(), name="get-dataset-status")
]
