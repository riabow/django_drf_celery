"""
Celery configuration for payout_service project.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payout_service.settings')

app = Celery('payout_service')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

