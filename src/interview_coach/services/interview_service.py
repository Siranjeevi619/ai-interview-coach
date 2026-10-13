from datetime import UTC, datetime
from typing import ClassVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from interview_coach.models.answer import Question
from interview_coach.models.interview import Interview, InterviewStatus
from interview_coach.repositories.answer_repository import AnswerRepository
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

    def generate_questions(self, interview_id: str) -> list[Question]:
        """Generate interview questions with Groq and persist them."""
        interview = self.get_or_404(interview_id)
        if interview.status in {InterviewStatus.completed, InterviewStatus.cancelled}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Questions cannot be generated for a finished interview",
            )
        answer_repository = AnswerRepository(self.repository.db)
        existing = answer_repository.list_questions(interview_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Questions have already been generated for this interview",
            )
        if not 1 <= interview.total_questions <= 20:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="AI generation supports between 1 and 20 questions",
            )
        try:
            from interview_coach.ai.question_generator import generate_questions

            generated = generate_questions(
                role=interview.role,
                difficulty=interview.difficulty.value,
                total_questions=interview.total_questions,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Question generation failed: {exc}",
            ) from exc

        questions = [
            Question(
                interview_id=interview_id,
                text=item.question_text,
                sequence_number=index,
                topic=item.topic,
            )
            for index, item in enumerate(generated.questions, start=1)
        ]
        for question in questions:
            self.repository.db.add(question)
        self.repository.db.commit()
        for question in questions:
            self.repository.db.refresh(question)
        return questions

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
