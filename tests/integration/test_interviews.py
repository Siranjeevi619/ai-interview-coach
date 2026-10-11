import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from interview_coach.database.base import Base
from interview_coach.database.session import get_db
from interview_coach.main import app


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def get_test_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_interview_workflow(client):
    interview = client.post(
        "/api/v1/interviews",
        json={"role": "Python Developer", "difficulty": "beginner", "total_questions": 2},
    )
    assert interview.status_code == 201
    interview_id = interview.json()["id"]

    question = client.post(
        f"/api/v1/interviews/{interview_id}/questions",
        json={"text": "What is a list?", "sequence_number": 1},
    )
    assert question.status_code == 201
    question_id = question.json()["id"]

    client.post(
        f"/api/v1/interviews/{interview_id}/questions",
        json={"text": "What is a tuple?", "sequence_number": 2},
    )
    assert client.post(f"/api/v1/interviews/{interview_id}/start").status_code == 200
    assert (
        client.post(
            f"/api/v1/questions/{question_id}/answers",
            json={"text": "A mutable collection."},
        ).status_code
        == 201
    )
    history = client.get(f"/api/v1/interviews/{interview_id}/history")
    assert [q["sequence_number"] for q in history.json()["questions"]] == [1, 2]
    assert len(history.json()["questions"][0]["answers"]) == 1
    assert client.post(f"/api/v1/interviews/{interview_id}/complete").status_code == 200
    assert (
        client.post(
            f"/api/v1/questions/{question_id}/answers",
            json={"text": "This must fail."},
        ).status_code
        == 409
    )


def test_validation_and_missing_interview(client):
    assert client.get("/api/v1/interviews/does-not-exist").status_code == 404
    response = client.post(
        "/api/v1/interviews",
        json={"role": "", "difficulty": "beginner", "total_questions": 0},
    )
    assert response.status_code == 422
