from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from interview_coach.database.session import get_db
from interview_coach.schemas.answer import AnswerCreate, AnswerResponse, QuestionResponse
from interview_coach.services.answer_service import AnswerService

router = APIRouter()


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: str, db: Session = Depends(get_db)):
    return AnswerService(db).get_question_or_404(question_id)


@router.post("/{question_id}/answers", response_model=AnswerResponse, status_code=201)
def add_answer(question_id: str, data: AnswerCreate, db: Session = Depends(get_db)):
    return AnswerService(db).add_answer(question_id, data)


@router.get("/{question_id}/answers", response_model=list[AnswerResponse])
def list_answers(question_id: str, db: Session = Depends(get_db)):
    service = AnswerService(db)
    service.get_question_or_404(question_id)
    return service.repository.list_answers(question_id)
