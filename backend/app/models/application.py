from sqlalchemy import String, Float, DateTime, JSON, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid, enum


class ApplicationStatus(str, enum.Enum):
    DISCOVERED = "discovered"
    SCORED     = "scored"
    QUEUED     = "queued"
    APPLYING   = "applying"
    SUBMITTED  = "submitted"
    TRACKING   = "tracking"
    VIEWED     = "viewed"
    INTERVIEW  = "interview"
    OFFER      = "offer"
    REJECTED   = "rejected"
    WITHDRAWN  = "withdrawn"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_url: Mapped[str] = mapped_column(String(1024))
    source_board: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    posted_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), index=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.DISCOVERED, index=True)

    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    match_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    strengths: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    gaps: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    resume_version: Mapped[int | None] = mapped_column(nullable=True)
    tailored_resume_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cover_letter_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    hiring_manager_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hiring_manager_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    applied_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status_change: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    job = relationship("Job", backref="applications", lazy="joined")
    user = relationship("User", backref="applications")
