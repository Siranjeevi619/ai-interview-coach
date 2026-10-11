from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from interview_coach.models.interview import Interview


class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, interview: Interview) -> Interview:
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def get(self, interview_id: str) -> Interview | None:
        return self.db.scalar(
            select(Interview)
            .options(joinedload(Interview.questions))
            .where(Interview.id == interview_id)
        )

    def list(self, offset: int, limit: int) -> tuple[list[Interview], int]:
        items = list(
            self.db.scalars(
                select(Interview).order_by(Interview.created_at.desc()).offset(offset).limit(limit)
            )
        )
        total = self.db.scalar(select(func.count()).select_from(Interview)) or 0
        return items, total

    def delete(self, interview: Interview) -> None:
        self.db.delete(interview)
        self.db.commit()
