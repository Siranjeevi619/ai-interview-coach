
from langchain_core.prompts import ChatPromptTemplate


question_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an experienced technical interviewer.

            Generate clear, relevant interview questions.
            Follow the requested role and difficulty.
            Do not provide answers or explanations.
            Avoid duplicate questions.
            """,
        ),
        (
            "human",
            """
            Generate {total_questions} interview questions.

            Job role: {role}
            Difficulty: {difficulty}

            Return the questions as a numbered list.
            """,
        ),
    ]
)
