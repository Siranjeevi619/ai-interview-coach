from fastapi import FastAPI

from interview_coach.api.router import router

app = FastAPI(title="AI Interview Coach", version="1.0.0")

app.include_router(router=router, prefix="/api/v1")
