# celery_app.py
from celery import Celery
from app.core.config import BROKER_URL

celery_app = Celery(
    'ingestion_pipeline',
    broker=BROKER_URL,
    include=['tasks']
)

# Optional configurations
celery_app.conf.update(
    result_expires=3600,  # Results expire after 1 hour
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
)
