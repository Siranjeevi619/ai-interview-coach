from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from interview_coach.schemas.interview import InterviewResponse


class QuestionCreate(BaseModel):
    text: str = Field(min_length=1)
    sequence_number: int = Field(ge=1)
    topic: str | None = Field(default=None, max_length=120)


class AnswerCreate(BaseModel):
    text: str = Field(min_length=1)


class AnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    question_id: str
    text: str
    created_at: datetime


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_id: str
    text: str
    sequence_number: int
    topic: str | None
    created_at: datetime
    answers: list[AnswerResponse] = []


class HistoryResponse(BaseModel):
    interview: InterviewResponse
    questions: list[QuestionResponse]
