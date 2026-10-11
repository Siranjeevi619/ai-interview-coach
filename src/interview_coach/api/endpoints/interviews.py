from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from interview_coach.database.session import get_db
from interview_coach.models.interview import InterviewStatus
from interview_coach.schemas.answer import HistoryResponse, QuestionCreate, QuestionResponse
from interview_coach.schemas.interview import (
    InterviewCreate,
    InterviewListResponse,
    InterviewResponse,
    InterviewUpdate,
)
from interview_coach.services.answer_service import AnswerService
from interview_coach.services.interview_service import InterviewService

router = APIRouter()


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    return InterviewService(db).create(data)


@router.get("", response_model=InterviewListResponse)
def list_interviews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = InterviewService(db).list(page, page_size)
    return InterviewListResponse(items=items, page=page, page_size=page_size, total=total)


@router.get("/{interview_id}", response_model=InterviewResponse)
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    return InterviewService(db).get_or_404(interview_id)


@router.patch("/{interview_id}", response_model=InterviewResponse)
def update_interview(interview_id: str, data: InterviewUpdate, db: Session = Depends(get_db)):
    return InterviewService(db).update(interview_id, data)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(interview_id: str, db: Session = Depends(get_db)):
    InterviewService(db).delete(interview_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def transition(target: InterviewStatus):
    def endpoint(interview_id: str, db: Session = Depends(get_db)):
        return InterviewService(db).transition(interview_id, target)

    return endpoint


router.add_api_route(
    "/{interview_id}/start",
    transition(InterviewStatus.in_progress),
    methods=["POST"],
    response_model=InterviewResponse,
)
router.add_api_route(
    "/{interview_id}/complete",
    transition(InterviewStatus.completed),
    methods=["POST"],
    response_model=InterviewResponse,
)
router.add_api_route(
    "/{interview_id}/cancel",
    transition(InterviewStatus.cancelled),
    methods=["POST"],
    response_model=InterviewResponse,
)


@router.post("/{interview_id}/questions", response_model=QuestionResponse, status_code=201)
def add_question(interview_id: str, data: QuestionCreate, db: Session = Depends(get_db)):
    return AnswerService(db).add_question(interview_id, data)


@router.get("/{interview_id}/questions", response_model=list[QuestionResponse])
def list_questions(interview_id: str, db: Session = Depends(get_db)):
    service = InterviewService(db)
    service.get_or_404(interview_id)
    return AnswerService(db).repository.list_questions(interview_id)


@router.get("/{interview_id}/history", response_model=HistoryResponse)
def history(interview_id: str, db: Session = Depends(get_db)):
    interview = InterviewService(db).get_or_404(interview_id)
    return {
        "interview": interview,
        "questions": AnswerService(db).repository.list_questions(interview_id),
    }
