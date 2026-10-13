#!/usr/bin/env python3
"""Check all 15 API endpoints with a full lifecycle workflow.

Usage:
  python scripts/check_endpoints.py           # isolated TestClient + PostgreSQL
  python scripts/check_endpoints.py --url http://127.0.0.1:8000  # live server
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def build_client(url: str | None):
    if url:
        import httpx

        return httpx.Client(base_url=url.rstrip("/"), timeout=10.0), False
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from interview_coach.core.config import settings
    from interview_coach.database.base import Base
    from interview_coach.database.session import get_db
    from interview_coach.main import app

    database_url = f"{settings.database_url.rsplit('/', 1)[0]}/interview_coach_test"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    return client, True


def main() -> int:
    parser = argparse.ArgumentParser(description="Check all 15 API endpoints.")
    parser.add_argument("--url", default=None, help="Live server URL, else uses isolated TestClient.")
    args = parser.parse_args()

    client, is_test = build_client(args.url)
    results: list[tuple[str, bool, str]] = []

    def check(name: str, method: str, path: str, expected: int, **kwargs):
        try:
            res = getattr(client, method)(path, **kwargs)
            ok = res.status_code == expected
            detail = f"got {res.status_code}, want {expected}"
            if not ok:
                try:
                    detail += f" body={res.text[:200]}"
                except Exception:
                    pass
            results.append((name, ok, f"{method.upper()} {path} -> {detail}"))
            return res if ok else None
        except Exception as exc:
            results.append((name, False, f"{method.upper()} {path} -> ERROR {exc}"))
            return None

    # 1. Health
    check("Health", "get", "/api/v1/health", 200)

    # 2. Create interview (main flow)
    r = check(
        "Create Interview", "post", "/api/v1/interviews", 201,
        json={"role": "Python Developer", "difficulty": "beginner", "total_questions": 2},
    )
    iid = r.json()["id"] if r else "missing"

    # 3-5. List / Get / Patch
    check("List Interviews", "get", "/api/v1/interviews", 200, params={"page": 1, "page_size": 20})
    check("Get Interview", "get", f"/api/v1/interviews/{iid}", 200)
    check("Update Interview", "patch", f"/api/v1/interviews/{iid}", 200,
          json={"role": "Senior Python Developer"})

    # 6-7. Add + List questions
    q1 = check(
        "Add Question", "post", f"/api/v1/interviews/{iid}/questions", 201,
        json={"text": "What is a list in Python?", "sequence_number": 1},
    )
    qid = q1.json()["id"] if q1 else "missing"
    check(
        "Add Question 2", "post", f"/api/v1/interviews/{iid}/questions", 201,
        json={"text": "What is a tuple?", "sequence_number": 2},
    )
    check("List Questions", "get", f"/api/v1/interviews/{iid}/questions", 200)

    # 8. Get question
    check("Get Question", "get", f"/api/v1/questions/{qid}", 200)

    # 9. Start
    check("Start Interview", "post", f"/api/v1/interviews/{iid}/start", 200)

    # 10-11. Add + List answers
    check(
        "Add Answer", "post", f"/api/v1/questions/{qid}/answers", 201,
        json={"text": "A list is an ordered, mutable collection."},
    )
    check("List Answers", "get", f"/api/v1/questions/{qid}/answers", 200)

    # 12. History
    check("History", "get", f"/api/v1/interviews/{iid}/history", 200)

    # 13. Complete
    check("Complete Interview", "post", f"/api/v1/interviews/{iid}/complete", 200)

    # 14. Cancel (needs fresh interview in created state)
    r2 = check(
        "Create for Cancel", "post", "/api/v1/interviews", 201,
        json={"role": "To Cancel", "difficulty": "beginner", "total_questions": 1},
    )
    if r2:
        check("Cancel Interview", "post", f"/api/v1/interviews/{r2.json()['id']}/cancel", 200)

    # 15. Delete (fresh interview, never started)
    r3 = check(
        "Create for Delete", "post", "/api/v1/interviews", 201,
        json={"role": "To Delete", "difficulty": "beginner", "total_questions": 1},
    )
    if r3:
        check("Delete Interview", "delete", f"/api/v1/interviews/{r3.json()['id']}", 204)

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{'PASS' if passed == len(results) else 'FAIL'}: {passed}/{len(results)} (mode={'TestClient' if is_test else 'live ' + args.url})")
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'} {name:<18} {detail}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
