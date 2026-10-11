# AI Interview Coach

AI-powered technical interview coach: resume-aware question generation,
answer evaluation, RAG over resumes/job descriptions, agentic interview
workflow, voice I/O hooks, and PDF/markdown reports.

## Layout

- `src/interview_coach/api/` — FastAPI router + endpoints (`health`, `interviews`, `resumes`, `reports`)
- `src/interview_coach/core/` — config + JWT security
- `src/interview_coach/schemas/` — Pydantic request/response models
- `src/interview_coach/models/` — SQLAlchemy ORM models
- `src/interview_coach/services/` — business logic
- `src/interview_coach/repositories/` — DB access layer
- `src/interview_coach/ai/` — LLM wrapper, prompts, generator, evaluator, structured outputs
- `src/interview_coach/rag/` — document loader, TF-IDF embeddings, in-memory retriever
- `src/interview_coach/agents/` — multi-step interview workflow state machine
- `src/interview_coach/voice/` — STT/TTS service interface
- `src/interview_coach/database/` — engine/session/base
- `tests/` — unit, integration, evaluation suites

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn interview_coach.main:app --reload
```

Open http://localhost:8000/docs for the API.

## API overview

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Liveness check |
| POST | `/api/v1/interviews` | Create interview session |
| GET | `/api/v1/interviews/{id}` | Get interview + answers |
| POST | `/api/v1/interviews/{id}/next-question` | Generate next question |
| POST | `/api/v1/interviews/{id}/answers` | Submit + evaluate answer |
| POST | `/api/v1/resumes/upload` | Upload + index resume |
| GET | `/api/v1/reports/{interview_id}` | JSON report |
| GET | `/api/v1/reports/{interview_id}/download` | Markdown report download |

## Notes

- No `OPENAI_API_KEY`? The AI layer falls back to deterministic
  template-based questions and rubric scoring so tests run offline.
- Default DB is SQLite. Set `DATABASE_URL` for Postgres.
- Run tests: `pytest -q`.
