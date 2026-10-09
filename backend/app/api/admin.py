
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Student, Job, Application, TrainingSession
from app.dependencies import require_roles
from app.services.csv_import import import_students

router = APIRouter(prefix="/api/admin", tags=["College Admin"])


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    return {
        "students": db.query(Student).count(),
        "jobs_pending": db.query(Job).filter(Job.status == "pending").count(),
        "jobs_approved": db.query(Job).filter(Job.status == "approved").count(),
        "applications": db.query(Application).count(),
        "training_sessions": db.query(TrainingSession).count()
    }


@router.post("/import-students")
def upload_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file")

    try:
        result = import_students(file.file, db)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="CSV import failed")
    finally:
        file.file.close()


@router.get("/jobs/pending")
def pending_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    jobs = db.query(Job).filter(Job.status == "pending").all()
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
        for j in jobs
    ]


@router.post("/jobs/{job_id}/approve")
def approve_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "approved"
    db.commit()
    return {"message": "Job approved"}


@router.post("/jobs/{job_id}/reject")
def reject_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "rejected"
    db.commit()
    return {"message": "Job rejected"}