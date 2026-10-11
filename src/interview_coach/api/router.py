from fastapi.routing import APIRouter

from interview_coach.api.endpoints import health, interviews, questions

router = APIRouter()
router.include_router(health.router, prefix="/health")
router.include_router(interviews.router, prefix="/interviews", tags=["interviews"])
router.include_router(questions.router, prefix="/questions", tags=["questions"])
