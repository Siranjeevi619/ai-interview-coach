from fastapi.routing import APIRoute, APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}

