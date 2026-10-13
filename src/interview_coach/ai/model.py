from langchain_groq import ChatGroq

from interview_coach.core.config import settings

if not settings.groq_api_key or not settings.groq_model:
    raise RuntimeError(
        "Groq configuration is missing. "
        "Set GROQ_API_KEY and GROQ_MODEL in your .env file."
    )

llm = ChatGroq(
    model=settings.groq_model,
    api_key=settings.groq_api_key,
    temperature=0.2,
    timeout=30,
    max_retries=2,
)
