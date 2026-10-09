import json
from typing import List, Optional, Union
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Student, User, AutoApplyReceipt, Application, Job
from app.dependencies import require_roles
from app.services.eligibility import parse_skills
from app.agent.auto_apply_graph import auto_apply_agent_graph

router = APIRouter(prefix="/api/auto-apply", tags=["LangGraph Autonomous Auto-Apply Agent"])


class AutoApplyRequest(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    job_url: Optional[str] = ""
    required_skills: Optional[Union[List[str], str]] = []


@router.post("/job")
def auto_apply_to_job(
    payload: AutoApplyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    """
    Invokes the LangGraph state machine agent to autonomously:
    1. Evaluate eligibility & technical fit against student profile.
    2. Tailor open-source Hugging Face cover letter and answers.
    3. Execute automated application submission and generate official receipt.
    """
    student = db.query(Student).filter(Student.email == user.email).first()

    # Graceful fallback: if no Student row linked to this user, build minimal profile from user data
    if not student:
        # Try to find by name if email doesn't match (import scenario)
        student = db.query(Student).filter(Student.name == user.name).first()

    if student:
        student_skills_raw = parse_skills(student.skills or "")
        s_id = student.id
        s_name = student.name
        s_email = student.email
        s_roll = student.roll_number
        s_branch = student.branch or "Engineering"
        s_cgpa = float(student.cgpa or 7.0)
    else:
        # No student record at all — use user account details, treat as general applicant
        student_skills_raw = []
        s_id = user.id
        s_name = user.name or user.email.split("@")[0]
        s_email = user.email
        s_roll = f"USR-{user.id}"
        s_branch = "Engineering"
        s_cgpa = 7.0  # default neutral CGPA so they aren't blocked

    # Parse required skills
    if isinstance(payload.required_skills, str):
        req_skills = parse_skills(payload.required_skills)
    elif isinstance(payload.required_skills, list):
        req_skills = payload.required_skills
    else:
        req_skills = []

    # Initial State for LangGraph
    initial_state = {
        "student_id": s_id,
        "student_name": s_name,
        "student_email": s_email,
        "student_roll": s_roll,
        "student_branch": s_branch,
        "student_cgpa": s_cgpa,
        "student_skills": student_skills_raw,
        "job_id": str(payload.job_id),
        "job_title": payload.job_title,
        "company_name": payload.company_name,
        "job_url": payload.job_url or "",
        "required_skills": req_skills,
        "match_score": 0.0,
        "eligible": False,
        "tailored_cover_letter": "",
        "custom_qa": {},
        "application_status": "initiated",
        "receipt": {},
        "error_message": ""
    }

    # Execute LangGraph Workflow
    try:
        final_state = auto_apply_agent_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangGraph execution error: {str(e)}")

    # Check if application was submitted
    receipt_data = final_state.get("receipt", {})
    status = "SUBMITTED" if final_state.get("eligible") else "INELIGIBLE_SKIPPED"
    confirmation_id = receipt_data.get("confirmation_id") or f"SKP-{s_id}-{payload.job_id}"

    # Persist receipt to DB
    existing_receipt = db.query(AutoApplyReceipt).filter(
        AutoApplyReceipt.student_id == s_id,
        AutoApplyReceipt.job_id == str(payload.job_id)
    ).first()

    if existing_receipt:
        existing_receipt.confirmation_id = confirmation_id
        existing_receipt.match_score = final_state.get("match_score", 0.0)
        existing_receipt.status = status
        existing_receipt.tailored_cover_letter = final_state.get("tailored_cover_letter", "")
        existing_receipt.custom_qa_json = json.dumps(final_state.get("custom_qa", {}))
        db.commit()
    else:
        new_receipt = AutoApplyReceipt(
            student_id=s_id,
            confirmation_id=confirmation_id,
            job_id=str(payload.job_id),
            job_title=payload.job_title,
            company_name=payload.company_name,
            portal_url=payload.job_url or "",
            match_score=final_state.get("match_score", 0.0),
            status=status,
            tailored_cover_letter=final_state.get("tailored_cover_letter", ""),
            custom_qa_json=json.dumps(final_state.get("custom_qa", {}))
        )
        db.add(new_receipt)
        db.commit()

    # If it's an on-campus job (numeric ID), also ensure Application row exists if eligible
    if str(payload.job_id).isdigit() and final_state.get("eligible") and student:
        numeric_job_id = int(payload.job_id)
        campus_job = db.query(Job).filter(Job.id == numeric_job_id).first()
        if campus_job:
            app_record = db.query(Application).filter(
                Application.student_id == s_id,
                Application.job_id == numeric_job_id
            ).first()
            if not app_record:
                app_record = Application(
                    student_id=s_id,
                    job_id=numeric_job_id,
                    status="applied"
                )
                db.add(app_record)
                db.commit()

    return {
        "success": final_state.get("eligible", False),
        "status": status,
        "confirmation_id": confirmation_id,
        "match_score": final_state.get("match_score", 0.0),
        "tailored_cover_letter": final_state.get("tailored_cover_letter", ""),
        "custom_qa": final_state.get("custom_qa", {}),
        "receipt": receipt_data,
        "execution_steps": [
            {"step": "evaluate_fit", "status": "COMPLETED", "eligible": final_state.get("eligible")},
            {"step": "huggingface_tailor", "status": "COMPLETED" if final_state.get("eligible") else "SKIPPED"},
            {"step": "execute_submission", "status": "COMPLETED" if final_state.get("eligible") else "SKIPPED"}
        ]
    }


@router.get("/receipts")
def list_student_auto_apply_receipts(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    """
    Returns all autonomous application receipts for the authenticated student.
    """
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        student = db.query(Student).filter(Student.name == user.name).first()

    # Use student.id if found, else fall back to user.id (matches what auto-apply stored)
    lookup_id = student.id if student else user.id

    receipts = db.query(AutoApplyReceipt).filter(
        AutoApplyReceipt.student_id == lookup_id
    ).order_by(AutoApplyReceipt.id.desc()).all()

    return [
        {
            "id": r.id,
            "confirmation_id": r.confirmation_id,
            "job_id": r.job_id,
            "job_title": r.job_title,
            "company_name": r.company_name,
            "portal_url": r.portal_url,
            "match_score": r.match_score,
            "status": r.status,
            "tailored_cover_letter": r.tailored_cover_letter,
            "custom_qa": json.loads(r.custom_qa_json or "{}"),
            "applied_at": r.applied_at,
            "created_at": r.applied_at  # alias for frontend compatibility
        }
        for r in receipts
    ]
