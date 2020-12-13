from django.urls import path
from csv_generator.views import ListSchemasView, \
    CreateSchemaView, DeleteSchemaView, UpdateSchemaView

app_name = "csv"

urlpatterns = [
    path('', ListSchemasView.as_view(), name='index'),
    path('schema/create/', CreateSchemaView.as_view(), name='schema-create'),
    path('schema/<int:pk>/delete', DeleteSchemaView.as_view(), name="schema-delete"),
    path('schema/<int:pk>', UpdateSchemaView.as_view(), name="schema-update")
]
