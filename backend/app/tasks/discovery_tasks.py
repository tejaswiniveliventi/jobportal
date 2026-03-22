import asyncio, logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.discovery_tasks.run_discovery_task")
def run_discovery_task(user_id: str = None):
    asyncio.run(_cycle(user_id))


async def _cycle(target_user_id: str = None):
    from app.database import AsyncSessionLocal
    from app.models.user import User
    from app.agents.orchestrator import run_orchestrator
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        q = select(User).where(User.is_active == True, User.profile_complete == True)
        if target_user_id:
            q = q.where(User.id == target_user_id)
        users = (await session.execute(q)).scalars().all()

    logger.info(f"[Discovery] running for {len(users)} users")
    for user in users:
        try:
            profile = {
                "user_id": user.id,
                "embedding_id": user.profile_embedding_id,
                "entities": user.profile_data or {},
            }
            state = await run_orchestrator(user.id, profile)
            await _persist(user.id, state.get("matched_jobs", []))
        except Exception as e:
            logger.error(f"[Discovery] user={user.id} error: {e}")


async def _persist(user_id: str, matched_jobs: list):
    from app.database import AsyncSessionLocal
    from app.models.application import Application, ApplicationStatus, Job
    from sqlalchemy import select, and_

    async with AsyncSessionLocal() as session:
        for jd in matched_jobs:
            sh = jd.get("source_hash")
            if not sh:
                continue
            r = await session.execute(select(Job).where(Job.source_hash == sh))
            job = r.scalar_one_or_none()
            if not job:
                job = Job(
                    source_hash=sh,
                    source_url=jd.get("source_url",""),
                    source_board=jd.get("source_board",""),
                    title=jd.get("title",""),
                    company=jd.get("company",""),
                    location=jd.get("location"),
                    is_remote=jd.get("is_remote", False),
                    description=(jd.get("description") or "")[:10000],
                    salary_min=jd.get("salary_min"),
                    salary_max=jd.get("salary_max"),
                )
                session.add(job)
                await session.flush()

            r2 = await session.execute(
                select(Application).where(and_(Application.user_id == user_id, Application.job_id == job.id))
            )
            if not r2.scalar_one_or_none():
                session.add(Application(
                    user_id=user_id, job_id=job.id,
                    status=ApplicationStatus.SCORED,
                    match_score=jd.get("match_score"),
                    match_reasoning=jd.get("match_reasoning"),
                    strengths=jd.get("strengths", []),
                    gaps=jd.get("gaps", []),
                ))
        await session.commit()
