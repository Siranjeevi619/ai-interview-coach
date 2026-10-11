from typing import Literal

from pydantic import BaseModel


class Question(BaseModel):
    question: str
    topic:str
    difficulty: Literal[
        "beginner",
        "intermediate",
        "expert",

    ]


class QuestionSet(BaseModel):
    question_list : list[Question]
