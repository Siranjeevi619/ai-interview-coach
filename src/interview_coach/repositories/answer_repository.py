from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from interview_coach.models.answer import Answer, Question


class AnswerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_question(self, question_id: str) -> Question | None:
        return self.db.scalar(
            select(Question)
            .options(joinedload(Question.interview))
            .where(Question.id == question_id)
        )

    def list_questions(self, interview_id: str) -> list[Question]:
        return list(
            self.db.scalars(
                select(Question)
                .options(joinedload(Question.answers))
                .where(Question.interview_id == interview_id)
                .order_by(Question.sequence_number)
            ).unique()
        )

    def create_question(self, question: Question) -> Question:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def create_answer(self, answer: Answer) -> Answer:
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def list_answers(self, question_id: str) -> list[Answer]:
        return list(
            self.db.scalars(
                select(Answer).where(Answer.question_id == question_id).order_by(Answer.created_at)
            )
        )
