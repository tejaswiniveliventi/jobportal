import asyncio, logging
from app.celery_app import celery_app
from app.agents.profile_agent import run_profile_agent

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.profile_tasks.process_resume_task",
                 max_retries=3, default_retry_delay=60)
def process_resume_task(self, user_id: str, file_path: str):
    try:
        logger.info(f"[ProfileTask] user={user_id}")
        profile = run_profile_agent(user_id, file_path)
        asyncio.run(_save_profile(user_id, profile))
        return {"status": "ok", "embed_id": profile["embedding_id"]}
    except Exception as exc:
        logger.error(f"[ProfileTask] failed: {exc}")
        raise self.retry(exc=exc)


async def _save_profile(user_id: str, profile: dict):
    from app.database import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        r = await session.execute(select(User).where(User.id == user_id))
        user = r.scalar_one_or_none()
        if user:
            user.profile_embedding_id = profile["embedding_id"]
            user.profile_data = profile.get("entities", {})
            user.profile_complete = True
            session.add(user)
            await session.commit()
