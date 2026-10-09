from typing import List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Student, User, Job, TrainingSession, Enrollment
from app.dependencies import require_roles
from app.services.eligibility import parse_skills
from app.services.faculty_agent import (
    evaluate_students_for_requirements,
    generate_shortlist_csv
)

router = APIRouter(prefix="/api/faculty", tags=["Faculty & Operator Autonomous Eligibility Agent"])


class EligibilityFilterRequest(BaseModel):
    job_id: Optional[int] = None
    company_name: Optional[str] = "Target Company"
    job_title: Optional[str] = "Job Role"
    minimum_cgpa: Optional[float] = 0.0
    eligible_branches: Optional[Union[List[str], str]] = []
    required_skills: Optional[Union[List[str], str]] = []
    graduation_year: Optional[int] = None
    min_skill_match_pct: Optional[float] = 0.0


@router.post("/filter-eligibility")
def filter_student_eligibility(
    payload: EligibilityFilterRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator", "training", "company"))
):
    """
    Autonomous Faculty Agent:
    Filters the entire student database (600+ records) against company requirements.
    """
    min_cgpa = payload.minimum_cgpa or 0.0
    grad_year = payload.graduation_year
    company = payload.company_name or "Target Company"
    title = payload.job_title or "Job Role"

    branches = []
    if isinstance(payload.eligible_branches, str):
        branches = [b.strip() for b in payload.eligible_branches.split(",") if b.strip()]
    elif isinstance(payload.eligible_branches, list):
        branches = payload.eligible_branches

    skills = []
    if isinstance(payload.required_skills, str):
        skills = parse_skills(payload.required_skills)
    elif isinstance(payload.required_skills, list):
        skills = payload.required_skills

    # If job_id is provided, merge with stored Job record
    if payload.job_id:
        job = db.query(Job).filter(Job.id == payload.job_id).first()
        if job:
            company = job.company_name
            title = job.title
            min_cgpa = max(min_cgpa, job.minimum_cgpa or 0.0)
            grad_year = grad_year or job.graduation_year
            if not branches and job.eligible_branches:
                branches = [b.strip() for b in job.eligible_branches.split(",") if b.strip()]
            if not skills and job.required_skills:
                skills = parse_skills(job.required_skills)

    result = evaluate_students_for_requirements(
        db=db,
        minimum_cgpa=min_cgpa,
        eligible_branches=branches,
        required_skills=skills,
        graduation_year=grad_year,
        min_skill_match_pct=payload.min_skill_match_pct or 0.0
    )

    return {
        "job_title": title,
        "company_name": company,
        "criteria_applied": {
            "minimum_cgpa": min_cgpa,
            "eligible_branches": branches,
            "required_skills": skills,
            "graduation_year": grad_year,
            "min_skill_match_pct": payload.min_skill_match_pct or 0.0
        },
        **result
    }


@router.post("/export-shortlist-csv")
def export_shortlist_to_csv(
    payload: EligibilityFilterRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator", "training", "company"))
):
    """
    Exports the filtered eligible candidate shortlist as an official CSV document.
    """
    min_cgpa = payload.minimum_cgpa or 0.0
    grad_year = payload.graduation_year
    company = payload.company_name or "Target Company"
    title = payload.job_title or "Job Role"

    branches = []
    if isinstance(payload.eligible_branches, str):
        branches = [b.strip() for b in payload.eligible_branches.split(",") if b.strip()]
    elif isinstance(payload.eligible_branches, list):
        branches = payload.eligible_branches

    skills = []
    if isinstance(payload.required_skills, str):
        skills = parse_skills(payload.required_skills)
    elif isinstance(payload.required_skills, list):
        skills = payload.required_skills

    if payload.job_id:
        job = db.query(Job).filter(Job.id == payload.job_id).first()
        if job:
            company = job.company_name
            title = job.title
            min_cgpa = max(min_cgpa, job.minimum_cgpa or 0.0)
            grad_year = grad_year or job.graduation_year
            if not branches and job.eligible_branches:
                branches = [b.strip() for b in job.eligible_branches.split(",") if b.strip()]
            if not skills and job.required_skills:
                skills = parse_skills(job.required_skills)

    eval_result = evaluate_students_for_requirements(
        db=db,
        minimum_cgpa=min_cgpa,
        eligible_branches=branches,
        required_skills=skills,
        graduation_year=grad_year,
        min_skill_match_pct=payload.min_skill_match_pct or 0.0
    )

    csv_data = generate_shortlist_csv(
        eligible_students=eval_result["eligible_students"],
        company_name=company,
        job_title=title
    )

    filename = f"Shortlist_{company.replace(' ', '_')}_{title.replace(' ', '_')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


class AutoEnrollRemediationRequest(BaseModel):
    skill: str
    target_job_title: str
    company_name: str
    student_ids: List[int]


@router.post("/auto-enroll-remediation")
def auto_enroll_students_in_remediation(
    payload: AutoEnrollRemediationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator", "training"))
):
    """
    Automatically creates a targeted skill gap remediation workshop and enrolls selected students.
    """
    if not payload.student_ids:
        raise HTTPException(status_code=400, detail="No students selected for enrollment.")

    session_title = f"{payload.skill.title()} Crash Workshop — Targeted for {payload.company_name}"
    
    # Check if session exists or create new
    session = db.query(TrainingSession).filter(TrainingSession.title == session_title).first()
    if not session:
        session = TrainingSession(
            title=session_title,
            description=f"Intensive technical remediation masterclass covering {payload.skill} for upcoming {payload.company_name} campus hiring drives.",
            trainer="Placement Technical Cell",
            capacity=max(100, len(payload.student_ids) + 20),
            created_by=user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    enrolled_count = 0
    for sid in payload.student_ids:
        existing = db.query(Enrollment).filter(
            Enrollment.student_id == sid,
            Enrollment.training_id == session.id
        ).first()
        if not existing:
            new_enrollment = Enrollment(
                student_id=sid,
                training_id=session.id,
                status="enrolled"
            )
            db.add(new_enrollment)
            enrolled_count += 1

    db.commit()

    return {
        "success": True,
        "message": f"Successfully enrolled {enrolled_count} students into '{session_title}'",
        "training_id": session.id,
        "training_title": session.title,
        "enrolled_count": enrolled_count
    }
