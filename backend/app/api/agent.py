from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Student, User, Job
from app.dependencies import require_roles
from app.agent import agent_instance

router = APIRouter(prefix="/api/agent", tags=["AI Placement Agent"])


class AgentChatRequest(BaseModel):
    job_id: int
    query: str = ""
    student_id: Optional[int] = None


@router.post("/chat")
def chat_with_agent(
    data: AgentChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student", "admin", "operator", "training", "company"))
):
    """
    Interactive Copilot Chat Endpoint:
    Provides intelligent interview prep coaching, mock questions, skill gap explanations, and roadmap synthesis.
    Works for Students and Administrators.
    """
    student = None
    if user.role == "student":
        student = db.query(Student).filter(Student.email == user.email).first()
    elif data.student_id:
        student = db.query(Student).filter(Student.id == data.student_id).first()
    else:
        student = db.query(Student).first()

    job = db.query(Job).filter(Job.id == data.job_id).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student profile or job not found")

    response = agent_instance.chat_interact(student, job, data.query)
    return response


@router.get("/diagnose/{job_id}")
def diagnose_job(
    job_id: int,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student", "admin", "operator", "training", "company"))
):
    student = None
    if user.role == "student":
        student = db.query(Student).filter(Student.email == user.email).first()
    elif student_id:
        student = db.query(Student).filter(Student.id == student_id).first()
    else:
        student = db.query(Student).first()

    job = db.query(Job).filter(Job.id == job_id).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student profile or job not found")

    analysis = agent_instance.analyze_profile(student, job)
    return analysis


@router.post("/prep-ecosystem")
def evaluate_prep_ecosystem(
    data: AgentChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student", "admin", "operator", "training", "company"))
):
    """
    Direct invocation of the Multi-Agent Prep Ecosystem StateGraph.
    Runs Master Orchestrator, Technical Examiner, STAR Bar-Raiser, and Adaptive Plan Rebalancer.
    """
    student = None
    if user.role == "student":
        student = db.query(Student).filter(Student.email == user.email).first()
    elif data.student_id:
        student = db.query(Student).filter(Student.id == data.student_id).first()
    else:
        student = db.query(Student).first()

    job = db.query(Job).filter(Job.id == data.job_id).first()

    if not student or not job:
        raise HTTPException(status_code=404, detail="Student profile or job not found")

    from app.agent.prep_agent_ecosystem import prep_agent_ecosystem_graph
    from app.services.eligibility import parse_skills

    initial_state = {
        "student_id": student.id,
        "student_name": student.name,
        "student_branch": getattr(student, "branch", "CSE"),
        "student_cgpa": float(getattr(student, "cgpa", 8.0) or 8.0),
        "student_skills": list(parse_skills(student.skills)),
        "job_id": job.id,
        "job_title": job.title,
        "company_name": job.company_name,
        "required_skills": list(parse_skills(job.required_skills)),
        "target_days": 30,
        "user_query": data.query or "comprehensive review",
        "routing_decision": "",
        "technical_assessment": {},
        "behavioral_assessment": {},
        "rebalanced_plan": {},
        "final_readiness_score": 0,
        "final_feedback_report": {},
        "final_response": ""
    }

    result = prep_agent_ecosystem_graph.invoke(initial_state)
    return {
        "readiness_score": result.get("final_readiness_score", 80),
        "report": result.get("final_feedback_report", {}),
        "summary_markdown": result.get("final_response", ""),
        "reply": result.get("final_response", "")
    }
