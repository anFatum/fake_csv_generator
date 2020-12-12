from django.urls import path
from csv_generator.views import index

app_name = "csv"

urlpatterns = [
    path('', index, name='index')
]
