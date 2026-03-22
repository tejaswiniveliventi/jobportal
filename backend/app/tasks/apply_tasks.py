import logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.apply_tasks.apply_to_job_task", bind=True, max_retries=2)
def apply_to_job_task(self, user_id: str, application_id: str):
    # Milestone 4: Playwright-based implementation
    logger.info(f"[ApplyTask] stub user={user_id} app={application_id}")
    return {"status": "stub"}
