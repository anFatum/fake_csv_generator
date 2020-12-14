import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fake_csv_generator.settings')
celery_app = Celery('fake_csv_generator')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()
