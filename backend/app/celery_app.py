from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "jobportal",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.profile_tasks",
        "app.tasks.discovery_tasks",
        "app.tasks.apply_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "discover-jobs-every-6h": {
            "task": "app.tasks.discovery_tasks.run_discovery_task",
            "schedule": 21600.0,
        },
    },
)
