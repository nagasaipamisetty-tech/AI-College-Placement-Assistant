from typing import List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Student, User, Job
from app.dependencies import require_roles
from app.services.eligibility import parse_skills
from app.services.latex_resume import (
    build_latex_resume_code,
    categorize_skills,
    generate_tailored_projects,
    escape_latex
)

router = APIRouter(prefix="/api/resume", tags=["Tailored LaTeX Resume Generator"])


class ResumeRequest(BaseModel):
    job_id: Optional[str] = ""
    job_title: Optional[str] = ""
    company_name: Optional[str] = ""
    required_skills: Optional[Union[List[str], str]] = []


@router.post("/generate-latex")
def generate_latex_resume(
    payload: ResumeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    """
    Generates an ATS-optimized, Jake's Resume style .tex file tailored dynamically
    to the target job role and company requirements.
    """
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    job_title = payload.job_title or "Software Development Engineer"
    company_name = payload.company_name or "Target Tech Company"
    req_skills = []

    # If numeric campus job ID provided, fill missing details from DB
    if payload.job_id and str(payload.job_id).isdigit():
        campus_job = db.query(Job).filter(Job.id == int(payload.job_id)).first()
        if campus_job:
            job_title = payload.job_title or campus_job.title
            company_name = payload.company_name or campus_job.company_name
            req_skills = parse_skills(campus_job.required_skills)

    if not req_skills:
        if isinstance(payload.required_skills, str):
            req_skills = parse_skills(payload.required_skills)
        elif isinstance(payload.required_skills, list):
            req_skills = payload.required_skills

    student_skills = parse_skills(student.skills)

    # Build LaTeX Code
    tex_code = build_latex_resume_code(
        name=student.name,
        email=student.email,
        roll_number=student.roll_number,
        branch=student.branch,
        cgpa=student.cgpa or 8.0,
        grad_year=student.graduation_year or 2027,
        job_title=job_title,
        company_name=company_name,
        required_skills=req_skills,
        student_skills=student_skills
    )

    clean_name = "".join(c for c in student.name if c.isalnum() or c == "_").replace(" ", "_")
    clean_company = "".join(c for c in company_name if c.isalnum() or c == "_").replace(" ", "_")
    filename = f"Resume_{clean_name}_{clean_company}.tex"

    categorized = categorize_skills(student_skills, req_skills)
    projects = generate_tailored_projects(job_title, company_name, student_skills)

    return {
        "filename": filename,
        "tex_content": tex_code,
        "job_title": job_title,
        "company_name": company_name,
        "preview": {
            "name": student.name,
            "email": student.email,
            "roll_number": student.roll_number,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "graduation_year": student.graduation_year or 2027,
            "categorized_skills": categorized,
            "projects": projects
        }
    }


@router.post("/download-tex")
def download_tex_file(
    payload: ResumeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    """
    Directly returns the .tex file as a downloadable attachment.
    """
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    job_title = payload.job_title or "Software Development Engineer"
    company_name = payload.company_name or "Target Tech Company"
    req_skills = []

    if payload.job_id and str(payload.job_id).isdigit():
        campus_job = db.query(Job).filter(Job.id == int(payload.job_id)).first()
        if campus_job:
            job_title = payload.job_title or campus_job.title
            company_name = payload.company_name or campus_job.company_name
            req_skills = parse_skills(campus_job.required_skills)

    if not req_skills:
        if isinstance(payload.required_skills, str):
            req_skills = parse_skills(payload.required_skills)
        elif isinstance(payload.required_skills, list):
            req_skills = payload.required_skills

    student_skills = parse_skills(student.skills)

    tex_code = build_latex_resume_code(
        name=student.name,
        email=student.email,
        roll_number=student.roll_number,
        branch=student.branch,
        cgpa=student.cgpa or 8.0,
        grad_year=student.graduation_year or 2027,
        job_title=job_title,
        company_name=company_name,
        required_skills=req_skills,
        student_skills=student_skills
    )

    clean_name = "".join(c for c in student.name if c.isalnum() or c == "_").replace(" ", "_")
    clean_company = "".join(c for c in company_name if c.isalnum() or c == "_").replace(" ", "_")
    filename = f"Resume_{clean_name}_{clean_company}.tex"

    return Response(
        content=tex_code,
        media_type="text/x-tex",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
