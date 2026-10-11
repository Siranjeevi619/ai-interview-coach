from datetime import UTC, datetime
from typing import ClassVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from interview_coach.models.interview import Interview, InterviewStatus
from interview_coach.repositories.interview_repository import InterviewRepository
from interview_coach.schemas.interview import InterviewCreate, InterviewUpdate


class InterviewService:
    transitions: ClassVar = {
        InterviewStatus.created: {
            InterviewStatus.in_progress,
            InterviewStatus.cancelled,
        },
        InterviewStatus.in_progress: {
            InterviewStatus.completed,
            InterviewStatus.cancelled,
        },
    }

    def __init__(self, db: Session):
        self.repository = InterviewRepository(db)

    def create(self, data: InterviewCreate) -> Interview:
        return self.repository.create(Interview(**data.model_dump()))

    def get_or_404(self, interview_id: str) -> Interview:
        interview = self.repository.get(interview_id)
        if interview is None:
            raise HTTPException(status_code=404, detail="Interview not found")
        return interview

    def list(self, page: int, page_size: int) -> tuple[list[Interview], int]:
        return self.repository.list((page - 1) * page_size, page_size)

    def update(self, interview_id: str, data: InterviewUpdate) -> Interview:
        interview = self.get_or_404(interview_id)
        if interview.status != InterviewStatus.created:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only a created interview can be updated",
            )
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(interview, field, value)
        self.repository.db.commit()
        self.repository.db.refresh(interview)
        return interview

    def delete(self, interview_id: str) -> None:
        interview = self.get_or_404(interview_id)
        if interview.status == InterviewStatus.in_progress:
            raise HTTPException(
                status_code=409, detail="An in-progress interview cannot be deleted"
            )
        self.repository.delete(interview)

    def transition(self, interview_id: str, target: InterviewStatus) -> Interview:
        interview = self.get_or_404(interview_id)
        if target not in self.transitions.get(interview.status, set()):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot change interview from {interview.status.value} to {target.value}",
            )
        now = datetime.now(UTC).replace(tzinfo=None)
        interview.status = target
        if target == InterviewStatus.in_progress:
            interview.started_at = now
        elif target == InterviewStatus.completed:
            interview.completed_at = now
        else:
            interview.cancelled_at = now
        self.repository.db.commit()
        self.repository.db.refresh(interview)
        return interview
