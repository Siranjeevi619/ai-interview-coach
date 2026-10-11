from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from interview_coach.models.interview import Difficulty, InterviewStatus


class InterviewCreate(BaseModel):
    role: str = Field(min_length=1, max_length=120)
    difficulty: Difficulty
    total_questions: int = Field(ge=1, le=100)


class InterviewUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=1, max_length=120)
    difficulty: Difficulty | None = None
    total_questions: int | None = Field(default=None, ge=1, le=100)


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    difficulty: Difficulty
    total_questions: int
    status: InterviewStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


class InterviewListResponse(BaseModel):
    items: list[InterviewResponse]
    page: int
    page_size: int
    total: int
