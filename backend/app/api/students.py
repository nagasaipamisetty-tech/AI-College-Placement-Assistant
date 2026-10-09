import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Student, User, Job, InterviewPrepPlan
from app.schemas import StudentCreate, StudentUpdate, StudentProfileUpdate
from app.core.security import hash_password
from app.dependencies import require_roles, get_current_user
from app.services.eligibility import check_eligibility
from app.services.matching import rank_jobs_for_student
from app.services.prep_planner import generate_interview_prep_plan
from sqlalchemy import or_, and_

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.post("/", status_code=201)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    """
    Allows Admin and Operator to manually add a new student.
    """
    clean_roll = data.roll_number.strip().upper()
    clean_email = data.email.strip().lower()

    existing_roll = db.query(Student).filter(Student.roll_number == clean_roll).first()
    if existing_roll:
        raise HTTPException(status_code=400, detail=f"Student with Roll Number '{clean_roll}' already exists.")

    existing_email = db.query(Student).filter(Student.email == clean_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail=f"Student with Email '{clean_email}' already exists.")

    new_student = Student(
        roll_number=clean_roll,
        name=data.name.strip(),
        email=clean_email,
        phone=data.phone.strip() if data.phone else "",
        branch=data.branch.strip().upper(),
        graduation_year=data.graduation_year or 2026,
        cgpa=data.cgpa if data.cgpa is not None else 0.0,
        skills=data.skills.strip(),
        linkedin_url=data.linkedin_url.strip() if data.linkedin_url else "",
        github_url=data.github_url.strip() if data.github_url else "",
        hackerrank_url=data.hackerrank_url.strip() if data.hackerrank_url else "",
        leetcode_url=data.leetcode_url.strip() if data.leetcode_url else "",
        portfolio_url=data.portfolio_url.strip() if data.portfolio_url else "",
        bio=data.bio.strip() if data.bio else "",
        approved_for_registration=True
    )
    db.add(new_student)

    # Ensure a corresponding student User account exists
    user_acc = db.query(User).filter(User.email == clean_email).first()
    if not user_acc:
        new_user = User(
            name=data.name.strip(),
            email=clean_email,
            password_hash=hash_password("password123"),
            role="student",
            is_active=True
        )
        db.add(new_user)

    db.commit()
    db.refresh(new_student)

    return {
        "id": new_student.id,
        "roll_number": new_student.roll_number,
        "name": new_student.name,
        "email": new_student.email,
        "phone": new_student.phone,
        "branch": new_student.branch,
        "graduation_year": new_student.graduation_year,
        "cgpa": new_student.cgpa,
        "skills": new_student.skills,
        "linkedin_url": new_student.linkedin_url,
        "github_url": new_student.github_url,
        "hackerrank_url": new_student.hackerrank_url,
        "leetcode_url": new_student.leetcode_url,
        "portfolio_url": new_student.portfolio_url,
        "bio": new_student.bio,
        "message": "Student created successfully"
    }


@router.get("/me")
def my_student_profile(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(
        Student.email == user.email
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "branch": student.branch,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "skills": student.skills,
        "linkedin_url": student.linkedin_url,
        "github_url": student.github_url,
        "hackerrank_url": student.hackerrank_url,
        "leetcode_url": student.leetcode_url,
        "portfolio_url": student.portfolio_url,
        "bio": student.bio
    }


@router.put("/me")
def update_my_student_profile(
    data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(
        Student.email == user.email
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    if data.phone is not None:
        student.phone = data.phone.strip()

    if data.skills is not None:
        student.skills = data.skills.strip()

    if data.linkedin_url is not None:
        student.linkedin_url = data.linkedin_url.strip()

    if data.github_url is not None:
        student.github_url = data.github_url.strip()

    if data.hackerrank_url is not None:
        student.hackerrank_url = data.hackerrank_url.strip()

    if data.leetcode_url is not None:
        student.leetcode_url = data.leetcode_url.strip()

    if data.portfolio_url is not None:
        student.portfolio_url = data.portfolio_url.strip()

    if data.bio is not None:
        student.bio = data.bio.strip()

    db.commit()
    db.refresh(student)

    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "branch": student.branch,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "skills": student.skills,
        "linkedin_url": student.linkedin_url,
        "github_url": student.github_url,
        "hackerrank_url": student.hackerrank_url,
        "leetcode_url": student.leetcode_url,
        "portfolio_url": student.portfolio_url,
        "bio": student.bio,
        "message": "Student profile updated successfully"
    }


@router.put("/{student_id}")
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    """
    Allows Admin and Operator to edit student details.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    old_email = student.email

    if data.roll_number is not None:
        clean_roll = data.roll_number.strip().upper()
        conflict = db.query(Student).filter(Student.roll_number == clean_roll, Student.id != student_id).first()
        if conflict:
            raise HTTPException(status_code=400, detail=f"Roll Number '{clean_roll}' already assigned to another student.")
        student.roll_number = clean_roll

    if data.name is not None:
        student.name = data.name.strip()

    if data.email is not None:
        clean_email = data.email.strip().lower()
        conflict = db.query(Student).filter(Student.email == clean_email, Student.id != student_id).first()
        if conflict:
            raise HTTPException(status_code=400, detail=f"Email '{clean_email}' already assigned to another student.")
        student.email = clean_email
        
        user_acc = db.query(User).filter(User.email == old_email).first()
        if user_acc:
            user_acc.email = clean_email
            user_acc.name = student.name

    if data.phone is not None:
        student.phone = data.phone.strip()

    if data.branch is not None:
        student.branch = data.branch.strip().upper()

    if data.graduation_year is not None:
        student.graduation_year = data.graduation_year

    if data.cgpa is not None:
        student.cgpa = data.cgpa

    if data.skills is not None:
        student.skills = data.skills.strip()

    if data.linkedin_url is not None:
        student.linkedin_url = data.linkedin_url.strip()

    if data.github_url is not None:
        student.github_url = data.github_url.strip()

    if data.hackerrank_url is not None:
        student.hackerrank_url = data.hackerrank_url.strip()

    if data.leetcode_url is not None:
        student.leetcode_url = data.leetcode_url.strip()

    if data.portfolio_url is not None:
        student.portfolio_url = data.portfolio_url.strip()

    if data.bio is not None:
        student.bio = data.bio.strip()

    db.commit()
    db.refresh(student)

    return {
        "id": student.id,
        "roll_number": student.roll_number,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "branch": student.branch,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "skills": student.skills,
        "linkedin_url": student.linkedin_url,
        "github_url": student.github_url,
        "hackerrank_url": student.hackerrank_url,
        "leetcode_url": student.leetcode_url,
        "portfolio_url": student.portfolio_url,
        "bio": student.bio,
        "message": "Student details updated successfully"
    }


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator"))
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    db.delete(student)
    db.commit()
    return {"message": "Student record deleted successfully"}


@router.get("/")
def list_students(
    search: str = Query(default="", max_length=100),
    skill: Optional[str] = Query(default=None),
    skills: Optional[list[str]] = Query(default=None),
    skill_mode: str = Query(default="all"),
    branch: Optional[str] = Query(default=None),
    min_cgpa: Optional[float] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator", "training", "company"))
):
    query = db.query(Student)

    # General multi-attribute search (including skills)
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Student.name.ilike(term))
            | (Student.roll_number.ilike(term))
            | (Student.email.ilike(term))
            | (Student.branch.ilike(term))
            | (Student.skills.ilike(term))
        )

    # Dedicated single or multi-skill filter
    skill_items = []
    if skill and skill.strip():
        skill_items.extend([s.strip() for s in skill.split(",") if s.strip()])
    if skills:
        for s in skills:
            if s and s.strip():
                skill_items.extend([x.strip() for x in s.split(",") if x.strip()])
    
    unique_skills = []
    for s in skill_items:
        if s.lower() not in [u.lower() for u in unique_skills]:
            unique_skills.append(s)

    if unique_skills:
        if skill_mode == "any":
            query = query.filter(or_(*[Student.skills.ilike(f"%{s}%") for s in unique_skills]))
        else: # default "all"
            for s in unique_skills:
                query = query.filter(Student.skills.ilike(f"%{s}%"))

    # Branch filter
    if branch and branch.strip() and branch != "all":
        query = query.filter(Student.branch.ilike(f"%{branch.strip()}%"))

    # Min CGPA filter
    if min_cgpa is not None and min_cgpa > 0:
        query = query.filter(Student.cgpa >= float(min_cgpa))

    students = query.order_by(Student.cgpa.desc(), Student.name).limit(500).all()

    return [
        {
            "id": s.id,
            "roll_number": s.roll_number,
            "name": s.name,
            "email": s.email,
            "phone": s.phone,
            "branch": s.branch,
            "graduation_year": s.graduation_year,
            "cgpa": s.cgpa,
            "skills": s.skills,
            "linkedin_url": s.linkedin_url,
            "github_url": s.github_url,
            "hackerrank_url": s.hackerrank_url,
            "leetcode_url": s.leetcode_url,
            "portfolio_url": s.portfolio_url,
            "bio": s.bio
        }
        for s in students
    ]


@router.get("/me/eligibility/{job_id}")
def my_eligibility(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Students only")

    student = db.query(Student).filter(
        Student.email == user.email
    ).first()
    job = db.query(Job).filter(
        Job.id == job_id, Job.status == "approved"
    ).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or job not found")

    return check_eligibility(student, job)


@router.get("/me/matched-jobs")
def my_matched_jobs(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    approved_jobs = db.query(Job).filter(Job.status == "approved").all()
    ranked_results = rank_jobs_for_student(student, approved_jobs)
    return ranked_results


@router.post("/me/prep-plan/{job_id}", status_code=200)
def generate_or_get_prep_plan(
    job_id: int,
    days: Optional[int] = Query(default=None),
    drive_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.email == user.email).first()
    job = db.query(Job).filter(Job.id == job_id, Job.status == "approved").first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or approved job not found")

    plan_dict = generate_interview_prep_plan(student, job, target_days=days, drive_date=drive_date)

    existing = db.query(InterviewPrepPlan).filter(
        InterviewPrepPlan.student_id == student.id,
        InterviewPrepPlan.job_id == job.id
    ).first()

    skill_gaps_str = ", ".join(plan_dict.get("missing_skills", []))
    plan_json_str = json.dumps(plan_dict)

    if existing:
        existing.skill_gaps = skill_gaps_str
        existing.skill_match_percentage = plan_dict.get("skill_match_percentage", 0.0)
        existing.plan_json = plan_json_str
        db.commit()
    else:
        new_plan = InterviewPrepPlan(
            student_id=student.id,
            job_id=job.id,
            skill_gaps=skill_gaps_str,
            skill_match_percentage=plan_dict.get("skill_match_percentage", 0.0),
            plan_json=plan_json_str
        )
        db.add(new_plan)
        db.commit()

    return plan_dict


@router.get("/me/prep-plan/{job_id}")
def get_existing_prep_plan(
    job_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    plan_record = db.query(InterviewPrepPlan).filter(
        InterviewPrepPlan.student_id == student.id,
        InterviewPrepPlan.job_id == job_id
    ).first()

    if not plan_record:
        raise HTTPException(status_code=404, detail="Preparation plan not generated yet")

    return json.loads(plan_record.plan_json)


@router.get("/me/prep-plans")
def list_my_prep_plans(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    plans = db.query(InterviewPrepPlan).filter(
        InterviewPrepPlan.student_id == student.id
    ).order_by(InterviewPrepPlan.id.desc()).all()

    results = []
    for p in plans:
        job = db.query(Job).filter(Job.id == p.job_id).first()
        results.append({
            "id": p.id,
            "job_id": p.job_id,
            "job_title": job.title if job else "Unknown",
            "company_name": job.company_name if job else "Unknown",
            "skill_match_percentage": p.skill_match_percentage,
            "skill_gaps": p.skill_gaps,
            "created_at": p.created_at
        })

    return results


# ==============================================================================
# ADMIN / FACULTY / OPERATOR SPECIFIC STUDENT INSPECTION ENDPOINTS
# ==============================================================================

@router.get("/{student_id}/matched-jobs")
def get_student_matched_jobs_admin(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator", "training", "company"))
):
    """
    Allows Admin/Faculty/Operator to view matched job drives and fit percentages for any student.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    approved_jobs = db.query(Job).filter(Job.status == "approved").all()
    ranked_results = rank_jobs_for_student(student, approved_jobs)
    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "roll_number": student.roll_number,
            "email": student.email,
            "branch": student.branch,
            "cgpa": student.cgpa,
            "skills": student.skills
        },
        "matches": ranked_results
    }


@router.post("/{student_id}/prep-plan/{job_id}")
def generate_student_prep_plan_admin(
    student_id: int,
    job_id: int,
    days: Optional[int] = Query(default=None),
    drive_date: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "operator", "training", "company"))
):
    """
    Allows Admin/Faculty to generate or view the dynamic N-day adaptive AI Prep Plan for any student.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    job = db.query(Job).filter(Job.id == job_id, Job.status == "approved").first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student or approved job not found")

    plan_dict = generate_interview_prep_plan(student, job, target_days=days, drive_date=drive_date)

    existing = db.query(InterviewPrepPlan).filter(
        InterviewPrepPlan.student_id == student.id,
        InterviewPrepPlan.job_id == job.id
    ).first()

    skill_gaps_str = ", ".join(plan_dict.get("missing_skills", []))
    plan_json_str = json.dumps(plan_dict)

    if existing:
        existing.skill_gaps = skill_gaps_str
        existing.skill_match_percentage = plan_dict.get("skill_match_percentage", 0.0)
        existing.plan_json = plan_json_str
        db.commit()
    else:
        new_plan = InterviewPrepPlan(
            student_id=student.id,
            job_id=job.id,
            skill_gaps=skill_gaps_str,
            skill_match_percentage=plan_dict.get("skill_match_percentage", 0.0),
            plan_json=plan_json_str
        )
        db.add(new_plan)
        db.commit()

    return plan_dict