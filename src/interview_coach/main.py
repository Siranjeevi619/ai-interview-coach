from fastapi import FastAPI

from interview_coach.api.router import router

app = FastAPI(
    title="Interview Coach",
    version="0.1.0",
)

app.include_router(router=router, prefix="/api/v1")