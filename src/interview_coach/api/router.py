from fastapi.routing import APIRoute, APIRouter

from interview_coach.api.endpoints import health

router = APIRouter()
router.include_router(health.router, prefix="/health")
