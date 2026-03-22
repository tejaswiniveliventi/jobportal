from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    profile_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    resume_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    profile_embedding_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    automation_settings: Mapped[dict | None] = mapped_column(
        JSON, nullable=True,
        default=lambda: {"auto_apply": False, "daily_limit": 5, "require_approval": True},
    )

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"
