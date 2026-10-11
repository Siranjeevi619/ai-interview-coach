from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from interview_coach.database.base import Base

if TYPE_CHECKING:
    from interview_coach.models.answer import Question
    from interview_coach.models.candidate import Candidate


class Difficulty(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class InterviewStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    candidate_id: Mapped[str | None] = mapped_column(ForeignKey("candidates.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(120))
    difficulty: Mapped[Difficulty] = mapped_column(SqlEnum(Difficulty, native_enum=False))
    total_questions: Mapped[int] = mapped_column(Integer)
    status: Mapped[InterviewStatus] = mapped_column(
        SqlEnum(InterviewStatus, native_enum=False), default=InterviewStatus.created
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    candidate: Mapped["Candidate | None"] = relationship(back_populates="interviews")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="Question.sequence_number",
    )
