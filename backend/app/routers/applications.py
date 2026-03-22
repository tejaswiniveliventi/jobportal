from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models.user import User
from app.models.application import Application, ApplicationStatus, Job
from app.core.deps import get_current_user
from app.schemas.application import ApplicationOut, ApplicationStatusUpdate, DashboardStats

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationOut])
async def list_applications(
    status: ApplicationStatus | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        select(Application)
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .limit(limit).offset(offset)
    )
    if status:
        q = q.where(Application.status == status)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = current_user.id

    async def count(where_clauses):
        r = await db.execute(select(func.count()).where(*where_clauses))
        return r.scalar() or 0

    total = await count([Application.user_id == uid])
    submitted = await count([Application.user_id == uid,
        Application.status.in_([ApplicationStatus.SUBMITTED, ApplicationStatus.TRACKING,
                                 ApplicationStatus.VIEWED, ApplicationStatus.INTERVIEW,
                                 ApplicationStatus.OFFER])])
    interviews = await count([Application.user_id == uid, Application.status == ApplicationStatus.INTERVIEW])
    offers = await count([Application.user_id == uid, Application.status == ApplicationStatus.OFFER])
    rejected = await count([Application.user_id == uid, Application.status == ApplicationStatus.REJECTED])

    response_rate = round((interviews + offers) / submitted * 100, 1) if submitted > 0 else 0.0

    top_r = await db.execute(
        select(Job.company, func.count(Application.id).label("count"))
        .join(Application, Application.job_id == Job.id)
        .where(Application.user_id == uid)
        .group_by(Job.company)
        .order_by(func.count(Application.id).desc())
        .limit(5)
    )
    top_companies = [{"company": r.company, "count": r.count} for r in top_r]

    weekly = []
    for i in range(6, -1, -1):
        day = datetime.now(timezone.utc) - timedelta(days=i)
        d0 = day.replace(hour=0, minute=0, second=0, microsecond=0)
        d1 = day.replace(hour=23, minute=59, second=59)
        c = await count([Application.user_id == uid,
                         Application.created_at >= d0, Application.created_at <= d1])
        weekly.append({"date": day.strftime("%a"), "applications": c})

    return DashboardStats(
        total_applications=total, submitted=submitted,
        interviews=interviews, offers=offers, rejected=rejected,
        response_rate=response_rate, top_companies=top_companies, weekly_activity=weekly,
    )


@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(and_(Application.id == app_id, Application.user_id == current_user.id))
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(404, "Application not found")
    return app


@router.patch("/{app_id}/status", response_model=ApplicationOut)
async def update_status(
    app_id: str,
    payload: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Application).where(and_(Application.id == app_id, Application.user_id == current_user.id))
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(404, "Application not found")
    app.status = payload.status
    app.last_status_change = datetime.now(timezone.utc)
    db.add(app)
    return app
