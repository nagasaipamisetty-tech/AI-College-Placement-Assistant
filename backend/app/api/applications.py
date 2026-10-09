
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Student, Job, Application
from app.schemas import ApplicationCreate, ApplicationStatusUpdate, AdminApplicationCreate
from app.dependencies import get_current_user, require_roles
from app.services.eligibility import check_eligibility

router = APIRouter(prefix="/api/applications", tags=["Applications"])


@router.post("/override-apply", status_code=201)
def override_apply_for_job(
    data: AdminApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    """
    Allows Admin and Operator to directly enroll/nominate any student into a drive,
    bypassing all CGPA, branch, or skill eligibility constraints.
    """
    student = db.query(Student).filter(Student.id == data.student_id).first()
    job = db.query(Job).filter(Job.id == data.job_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    if not job:
        raise HTTPException(status_code=404, detail="Job drive not found")

    existing = db.query(Application).filter(
        Application.student_id == student.id,
        Application.job_id == job.id
    ).first()

    status_to_set = data.status if data.status in {"applied", "shortlisted", "interview", "selected"} else "applied"

    if existing:
        existing.status = status_to_set
        db.commit()
        db.refresh(existing)
        return {
            "id": existing.id,
            "message": f"Student '{student.name}' is already in this drive. Status updated to '{existing.status}'.",
            "overridden": True
        }

    application = Application(
        student_id=student.id,
        job_id=job.id,
        status=status_to_set
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "id": application.id,
        "message": f"Student '{student.name}' successfully enrolled in drive '{job.title} - {job.company_name}' (Eligibility Override Active).",
        "overridden": True
    }


@router.post("/", status_code=201)
def apply_for_job(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(
        Student.email == user.email
    ).first()
    job = db.query(Job).filter(
        Job.id == data.job_id, Job.status == "approved"
    ).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or approved job not found")

    eligibility = check_eligibility(student, job)
    if not eligibility["eligible"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "You do not meet all job requirements",
                "reasons": eligibility["reasons"]
            }
        )

    existing = db.query(Application).filter(
        Application.student_id == student.id,
        Application.job_id == job.id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Already applied")

    application = Application(
        student_id=student.id,
        job_id=job.id,
        status="applied"
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return {"id": application.id, "message": "Application submitted"}


@router.get("/mine")
def my_applications(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(
        Student.email == user.email
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    records = db.query(Application).filter(
        Application.student_id == student.id
    ).all()

    result = []
    for record in records:
        job = db.query(Job).filter(Job.id == record.job_id).first()
        result.append({
            "id": record.id,
            "job_id": record.job_id,
            "job_title": job.title if job else "Deleted job",
            "company_name": job.company_name if job else "",
            "status": record.status
        })

    return result


@router.get("/")
def list_applications(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    records = db.query(Application).order_by(Application.id.desc()).all()
    result = []

    for record in records:
        student = db.query(Student).filter(
            Student.id == record.student_id
        ).first()
        job = db.query(Job).filter(Job.id == record.job_id).first()

        result.append({
            "id": record.id,
            "student_name": student.name if student else "",
            "roll_number": student.roll_number if student else "",
            "job_title": job.title if job else "",
            "company_name": job.company_name if job else "",
            "status": record.status
        })

    return result


@router.patch("/{application_id}/status")
def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    allowed = {"applied", "shortlisted", "interview", "selected", "rejected"}

    if data.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")

    record = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Application not found")

    record.status = data.status
    db.commit()
    return {"message": "Application status updated"}