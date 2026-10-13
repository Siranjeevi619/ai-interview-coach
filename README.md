# AI Interview Coach

This project is the backend foundation for an interview practice application.
Phase 1 and Phase 2 deliberately do **not** use an LLM. They teach the data
flow first: create an interview, add questions, save answers, and manage the
interview lifecycle.

## How the code is organised

The request travels through a few small layers:

```text
Client
  -> FastAPI endpoint (HTTP details and status codes)
  -> service (business rules such as lifecycle transitions)
  -> repository (SQLAlchemy queries)
  -> PostgreSQL
```

The response travels back through the same layers. Pydantic schemas decide
what enters and leaves the API, so database objects are never returned
directly. The `ai`, `rag`, `agents`, and `voice` folders are placeholders for
later phases and are not used yet.

## Concepts used here

- An environment variable is a value supplied outside Python, such as a
  database password. It keeps secrets out of source control.
- PostgreSQL is the database server. A database contains tables; a table
  contains rows; a row is one record; and a column is one property.
- A primary key uniquely identifies a row. A foreign key connects one table to
  another. For example, `questions.interview_id` points to an interview.
- SQLAlchemy maps Python classes to tables. A database session is a short-lived
  connection used by one request. FastAPI creates it with `get_db` and closes
  it after the request.
- Alembic is a migration tool. A migration is a versioned description of a
  database change, so a new application version does not erase existing data.
- Unit tests check one piece of logic. Integration tests exercise multiple
  layers together. The integration tests use a dedicated PostgreSQL database,
  never your development database.

## Setup

The project uses Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Install PostgreSQL on Ubuntu:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres psql
```

Inside `psql`, create the development user and database:

```sql
CREATE USER interview_coach WITH PASSWORD 'change-me';
CREATE DATABASE interview_coach OWNER interview_coach;
CREATE DATABASE interview_coach_test OWNER interview_coach;
\q
```

Put the matching connection URL in `.env`:

```text
DATABASE_URL=postgresql+psycopg://interview_coach:change-me@localhost:5432/interview_coach
```

The URL says: use PostgreSQL through the `psycopg` driver, connect as
`interview_coach`, use its password, connect to the local server on port 5432,
and open the `interview_coach` database. PostgreSQL is required; the
application rejects non-PostgreSQL database URLs.

## Migrations

Run the initial migration:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

When models change in a future phase, create and apply a new migration:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Do not call `Base.metadata.create_all()` on application startup in production.
Migrations make schema changes explicit and preserve old data.

## Run the application

```bash
python -m uvicorn interview_coach.main:app --reload --app-dir src
```

Open Swagger UI at <http://127.0.0.1:8000/docs>. The API prefix is
`/api/v1`.

## Available API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Check that the server is alive |
| POST | `/api/v1/interviews` | Create an interview |
| GET | `/api/v1/interviews` | List interviews with `page` and `page_size` |
| GET | `/api/v1/interviews/{id}` | Retrieve one interview |
| PATCH | `/api/v1/interviews/{id}` | Update a created interview |
| DELETE | `/api/v1/interviews/{id}` | Delete a non-running interview |
| POST | `/api/v1/interviews/{id}/start` | Move `created` to `in_progress` |
| POST | `/api/v1/interviews/{id}/complete` | Move `in_progress` to `completed` |
| POST | `/api/v1/interviews/{id}/cancel` | Cancel a created or running interview |
| POST | `/api/v1/interviews/{id}/questions` | Add a manual question |
| GET | `/api/v1/interviews/{id}/questions` | List questions in sequence order |
| GET | `/api/v1/questions/{id}` | Retrieve one question |
| POST | `/api/v1/questions/{id}/answers` | Add an answer attempt |
| GET | `/api/v1/questions/{id}/answers` | List answer attempts |
| GET | `/api/v1/interviews/{id}/history` | Retrieve interview, questions, and answers |

Questions may be added while an interview is `created` or `in_progress`, up to
`total_questions`. Answers are append-only attempts and can be submitted only
while the interview is `in_progress`. A completed interview cannot be
restarted or edited. Deleting an interview also deletes its questions and
answers through database cascade rules.

## Manual workflow

Create an interview:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/interviews \
  -H 'Content-Type: application/json' \
  -d '{"role":"Python Developer","difficulty":"beginner","total_questions":2}'
```

Copy the returned `id`, then add questions before or after starting:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/interviews/INTERVIEW_ID/questions \
  -H 'Content-Type: application/json' \
  -d '{"text":"What is a list in Python?","sequence_number":1}'

curl -X POST http://127.0.0.1:8000/api/v1/interviews/INTERVIEW_ID/start
```

Copy the question `id` and submit an answer:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/questions/QUESTION_ID/answers \
  -H 'Content-Type: application/json' \
  -d '{"text":"A list is an ordered, mutable collection."}'

curl http://127.0.0.1:8000/api/v1/interviews/INTERVIEW_ID/history
curl -X POST http://127.0.0.1:8000/api/v1/interviews/INTERVIEW_ID/complete
```

After completion, submitting another answer returns `409 Conflict`. Restarting
the server does not lose data because the records are stored in the database.

## Tests and debugging

```bash
pytest -q
ruff check src migrations tests
```

Common errors:

- `connection refused`: PostgreSQL is not running or the URL is wrong.
- `password authentication failed`: the `.env` password does not match the
  PostgreSQL user.
- `relation does not exist`: run `alembic upgrade head`.
- `404 Interview not found`: check the UUID copied from the create response.
- `409 Conflict`: the requested lifecycle action is not allowed in the
  interview's current state.

## Current limitations

There is no authentication, resume upload, AI question generation, answer
evaluation, RAG, voice support, or report generation yet. Those are
intentionally outside Phase 1 and Phase 2.

## Suggested learning order

1. Read `database/base.py` and `database/session.py`.
2. Read the three files in `models/` and compare foreign keys with
   relationships.
3. Read `schemas/` to see request validation and response shaping.
4. Follow `POST /interviews` through the endpoint, service, repository, and
   database.
5. Read the state transition method in `interview_service.py`.
6. Run the integration test and change one assertion at a time.
