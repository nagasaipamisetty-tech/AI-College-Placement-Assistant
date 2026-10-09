
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Job
from app.schemas import JobCreate
from app.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("/")
def list_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = db.query(Job)

    if user.role != "admin":
        query = query.filter(Job.status == "approved")

    return [
        {
            "id": j.id,
            "title": j.title,
            "company_name": j.company_name,
            "description": j.description,
            "required_skills": j.required_skills,
            "minimum_cgpa": j.minimum_cgpa,
            "eligible_branches": j.eligible_branches,
            "graduation_year": j.graduation_year,
            "status": j.status
        }
        for j in query.order_by(Job.id.desc()).all()
    ]


@router.post("/", status_code=201)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("company"))
):
    job = Job(
        **data.model_dump(),
        created_by=user.id,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "message": "Job submitted for college approval"}


@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job or (job.status != "approved" and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "description": job.description,
        "required_skills": job.required_skills,
        "minimum_cgpa": job.minimum_cgpa,
        "eligible_branches": job.eligible_branches,
        "graduation_year": job.graduation_year,
        "status": job.status
    }