FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/
COPY migrations/ migrations/
COPY alembic.ini ./

RUN pip install --no-cache-dir -e .

ENV DATABASE_URL=postgresql+psycopg://interview_coach:change-me@host.docker.internal:5432/interview_coach
EXPOSE 8000

CMD ["uvicorn", "interview_coach.main:app", "--host", "0.0.0.0", "--port", "8000"]
