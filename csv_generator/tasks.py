import os
import shutil
import time
from pathlib import Path

import pandas as pd
from celery import shared_task
from django.core.files import File
from faker import Faker

from csv_generator.models import Dataset
from csv_generator.utils import user_directory_path
from fake_csv_generator import settings


@shared_task
def generate_dataset(dataset_pk):
    dataset = Dataset.objects.get(pk=dataset_pk)
    schema_fields = dataset.schema.fields.all()
    f = Faker()
    order_dict = {}
    result = pd.DataFrame()
    for field in schema_fields:
        method = getattr(f, str(field.field_type))
        order_dict[field.name] = field.order
        data = [method() for _ in range(dataset.rows)]
        if result.empty:
            result = pd.DataFrame({field.name: data})
        else:
            result = result.join(pd.DataFrame({field.name: data}))
    sorted_cols = sorted(result.columns, key=lambda x: order_dict[x])
    result = result[sorted_cols]
    timestamp = int(time.time())
    filename = f"dataset_{timestamp}.csv"
    output_path = user_directory_path(dataset, filename)
    output_path = settings.BASE_DIR / Path(output_path)
    os.makedirs(output_path.parent,
                exist_ok=True)
    result.to_csv(output_path,
                  quotechar=dataset.schema.string_character.character,
                  sep=dataset.schema.column_separator.character,
                  index=False)
    with open(output_path, 'rb') as f:
        dataset.file = File(f, filename)
        dataset.save()
    os.remove(output_path)
    shutil.rmtree(output_path.parent.parent)
    return dataset.file.url
