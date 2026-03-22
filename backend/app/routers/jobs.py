from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationStatus
from app.core.deps import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/discover", status_code=202)
async def trigger_discovery(current_user: User = Depends(get_current_user)):
    if not current_user.profile_complete:
        raise HTTPException(400, "Upload your resume first")
    from app.tasks.discovery_tasks import run_discovery_task
    run_discovery_task.delay(current_user.id)
    return {"message": "Discovery started — check back shortly"}


@router.post("/approve/{application_id}")
async def approve_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(
            and_(Application.id == application_id,
                 Application.user_id == current_user.id,
                 Application.status == ApplicationStatus.SCORED)
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(404, "Application not found or already processed")
    app.status = ApplicationStatus.QUEUED
    db.add(app)
    automation = current_user.automation_settings or {}
    if automation.get("auto_apply", False):
        from app.tasks.apply_tasks import apply_to_job_task
        apply_to_job_task.delay(current_user.id, application_id)
    return {"message": "Approved and queued"}


@router.post("/reject/{application_id}")
async def reject_application(
    application_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(
            and_(Application.id == application_id,
                 Application.user_id == current_user.id)
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(404, "Not found")
    app.status = ApplicationStatus.WITHDRAWN
    db.add(app)
    return {"message": "Application withdrawn"}
