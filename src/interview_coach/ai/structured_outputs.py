from typing import Literal

from pydantic import BaseModel, Field


class GeneratedQuestion(BaseModel):
    question_text: str = Field(
        description="The interview question shown to the candidate."
    )
    topic: str = Field(description="The technical topic being tested.")
    difficulty: Literal["beginner", "intermediate", "advanced"]


class GeneratedQuestionSet(BaseModel):
    questions: list[GeneratedQuestion]
