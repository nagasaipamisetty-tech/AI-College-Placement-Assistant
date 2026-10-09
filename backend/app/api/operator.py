from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Student, Job, Application, TrainingSession
from app.dependencies import require_roles

router = APIRouter(prefix="/api/operator", tags=["Operator"])


@router.get("/stats")
def operator_stats(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("operator", "admin"))
):
    return {
        "total_students": db.query(Student).count(),
        "approved_students": db.query(Student).filter(Student.approved_for_registration.is_(True)).count(),
        "pending_jobs": db.query(Job).filter(Job.status == "pending").count(),
        "approved_jobs": db.query(Job).filter(Job.status == "approved").count(),
        "total_applications": db.query(Application).count(),
        "training_sessions": db.query(TrainingSession).count()
    }


@router.get("/students")
def list_students_operator(
    search: str = Query(default="", max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("operator", "admin"))
):
    query = db.query(Student)

    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Student.name.ilike(term))
            | (Student.roll_number.ilike(term))
            | (Student.email.ilike(term))
            | (Student.branch.ilike(term))
        )

    students = query.order_by(Student.name).limit(500).all()
    return [
        {
            "id": s.id,
            "roll_number": s.roll_number,
            "name": s.name,
            "email": s.email,
            "branch": s.branch,
            "graduation_year": s.graduation_year,
            "cgpa": s.cgpa,
            "skills": s.skills,
            "approved_for_registration": s.approved_for_registration
        }
        for s in students
    ]


@router.post("/students/{student_id}/toggle-approval")
def toggle_student_approval(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("operator", "admin"))
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.approved_for_registration = not student.approved_for_registration
    db.commit()
    db.refresh(student)

    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "approved_for_registration": student.approved_for_registration,
        "message": f"Student approval status updated to {student.approved_for_registration}"
    }