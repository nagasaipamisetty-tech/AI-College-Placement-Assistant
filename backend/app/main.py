from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine, init_db
from app.core.config import settings

from app.api import (
    auth, students, admin, jobs,
    applications, training, operator, agent, live_jobs, auto_apply, resume, faculty_agent
)

init_db()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="College placement management API"
)

origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(admin.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(training.router)
app.include_router(operator.router)
app.include_router(agent.router)
app.include_router(live_jobs.router)
app.include_router(auto_apply.router)
app.include_router(resume.router)
app.include_router(faculty_agent.router)





@app.get("/")
def root():
    return {
        "message": "AI College Placement Assistant API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}