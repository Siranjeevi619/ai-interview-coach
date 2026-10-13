
from interview_coach.ai.model import llm
from interview_coach.ai.prompts.questions import question_prompt
from interview_coach.ai.structured_outputs import GeneratedQuestionSet
import logging
logger = logging.getLogger(__name__)


structured_llm = llm.with_structured_output(GeneratedQuestionSet)

question_chain = question_prompt | structured_llm

VALID_DIFFICULTIES = {
    "beginner",
    "intermediate",
    "advanced",
}


def validate_questions(
    result: GeneratedQuestionSet,
    role: str,
    difficulty: str,
    total_questions: int,
) -> None:
    if len(result.questions) != total_questions:
        raise ValueError(
            f"Expected {total_questions} questions, "
            f"but received {len(result.questions)}."
        )

    seen_questions = set()

    for question in result.questions:
        if not question.question_text.strip():
            raise ValueError("A question cannot be empty.")

        if not question.topic.strip():
            raise ValueError("A question topic cannot be empty.")

        if question.difficulty not in VALID_DIFFICULTIES:
            raise ValueError(
                f"Invalid difficulty: {question.difficulty}"
            )

        normalized_question = " ".join(
            question.question_text.lower().split()
        )

        if normalized_question in seen_questions:
            raise ValueError(
                f"Duplicate question detected: "
                f"{question.question_text}"
            )

        seen_questions.add(normalized_question)
        if question.difficulty != difficulty:
            raise ValueError(
                f"Expected difficulty '{difficulty}', "
                f"but received '{question.difficulty}'."
            )


async def generate_questions(
    role: str,
    difficulty: str,
    total_questions: int,
) -> GeneratedQuestionSet:
    if not role.strip():
        raise ValueError("Role cannot be empty.")

    if difficulty not in VALID_DIFFICULTIES:
        raise ValueError("Invalid difficulty level.")

    if not 1 <= total_questions <= 20:
        raise ValueError("Question count must be between 1 and 20.")

    logger.info(
        "Starting question generation: role=%s, difficulty=%s, count=%d",
        role,
        difficulty,
        total_questions,
    )

    try:
        result =  await question_chain.ainvoke(
            {
                "role": role,
                "difficulty": difficulty,
                "total_questions": total_questions,
            }
        )
    except Exception:
        logger.exception(
            "Question generation failed for role=%s, difficulty=%s",
            role,
            difficulty,
        )
        raise

    validate_questions(
        result=result,
        role=role,
        difficulty=difficulty,
        total_questions=total_questions,
    )

    logger.info(
        "Question generation succeeded: count=%d",
        len(result.questions),
    )

    return result

