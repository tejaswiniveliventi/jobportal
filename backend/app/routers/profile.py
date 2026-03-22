import os, uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.application import UserPreferencesUpdate, AutomationSettingsUpdate
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/profile", tags=["profile"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.get("", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/resume", status_code=202)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(422, "Only PDF and Word documents accepted")

    contents = await file.read()
    if len(contents) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb}MB")

    ext = os.path.splitext(file.filename or "resume.pdf")[1] or ".pdf"
    filename = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    dest = os.path.join(settings.upload_dir, filename)
    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(contents)

    current_user.resume_path = dest
    db.add(current_user)

    # Queue Profile Agent
    from app.tasks.profile_tasks import process_resume_task
    process_resume_task.delay(current_user.id, dest)

    return {"message": "Resume uploaded — processing started", "filename": filename}


@router.put("/preferences", response_model=UserResponse)
async def update_preferences(
    payload: UserPreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = current_user.preferences or {}
    current_user.preferences = {**existing, **payload.model_dump(exclude_none=True)}
    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.put("/automation", response_model=UserResponse)
async def update_automation(
    payload: AutomationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = current_user.automation_settings or {}
    current_user.automation_settings = {**existing, **payload.model_dump(exclude_none=True)}
    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return current_user
