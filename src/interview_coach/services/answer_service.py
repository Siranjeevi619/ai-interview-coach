from fastapi import HTTPException
from sqlalchemy.orm import Session

from interview_coach.models.answer import Answer, Question
from interview_coach.models.interview import Interview, InterviewStatus
from interview_coach.repositories.answer_repository import AnswerRepository
from interview_coach.schemas.answer import AnswerCreate, QuestionCreate


class AnswerService:
    def __init__(self, db: Session):
        self.repository = AnswerRepository(db)

    def add_question(self, interview_id: str, data: QuestionCreate) -> Question:
        questions = self.repository.list_questions(interview_id)
        if not questions:
            interview = self.repository.db.get(Interview, interview_id)
        else:
            interview = questions[0].interview
        if interview is None:
            raise HTTPException(status_code=404, detail="Interview not found")
        if interview.status in {InterviewStatus.completed, InterviewStatus.cancelled}:
            raise HTTPException(
                status_code=409, detail="Questions cannot be added to a finished interview"
            )
        if len(questions) >= interview.total_questions:
            raise HTTPException(
                status_code=409, detail="The interview already has its maximum questions"
            )
        if any(q.sequence_number == data.sequence_number for q in questions):
            raise HTTPException(
                status_code=409, detail="That question sequence number already exists"
            )
        return self.repository.create_question(
            Question(interview_id=interview_id, **data.model_dump())
        )

    def get_question_or_404(self, question_id: str) -> Question:
        question = self.repository.get_question(question_id)
        if question is None:
            raise HTTPException(status_code=404, detail="Question not found")
        return question

    def add_answer(self, question_id: str, data: AnswerCreate) -> Answer:
        question = self.get_question_or_404(question_id)
        if question.interview.status != InterviewStatus.in_progress:
            raise HTTPException(
                status_code=409, detail="Answers can only be submitted while in progress"
            )
        return self.repository.create_answer(Answer(question_id=question_id, text=data.text))
