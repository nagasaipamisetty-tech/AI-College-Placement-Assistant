import pytest
from app.agent.auto_apply_graph import auto_apply_agent_graph


def test_langgraph_auto_apply_workflow_eligible():
    initial_state = {
        "student_id": 1,
        "student_name": "Test Candidate",
        "student_email": "candidate@college.edu",
        "student_roll": "23CS001",
        "student_branch": "Computer Science and Engineering",
        "student_cgpa": 8.8,
        "student_skills": ["Python", "FastAPI", "React", "Docker", "SQL"],
        "job_id": "live-uber-1",
        "job_title": "Software Engineer - Distributed Systems",
        "company_name": "Uber",
        "job_url": "https://uber.com/careers/test",
        "required_skills": ["Python", "Docker", "FastAPI"],
        "match_score": 0.0,
        "eligible": False,
        "tailored_cover_letter": "",
        "custom_qa": {},
        "application_status": "initiated",
        "receipt": {},
        "error_message": ""
    }

    result = auto_apply_agent_graph.invoke(initial_state)

    assert result["eligible"] is True
    assert result["match_score"] == 100
    assert result["application_status"] == "submitted_successfully"
    assert "receipt" in result
    assert result["receipt"]["confirmation_id"].startswith("APP-")
    assert result["receipt"]["company_name"] == "Uber"
    assert len(result["tailored_cover_letter"]) > 20
    assert "Why do you want to join Uber?" in result["custom_qa"]


def test_langgraph_auto_apply_workflow_ineligible():
    initial_state = {
        "student_id": 2,
        "student_name": "Junior Student",
        "student_email": "junior@college.edu",
        "student_roll": "23ME001",
        "student_branch": "Mechanical Engineering",
        "student_cgpa": 5.0,  # Below threshold
        "student_skills": ["AutoCAD", "Thermodynamics"],
        "job_id": "live-google-1",
        "job_title": "Cloud Architect",
        "company_name": "Google",
        "job_url": "https://google.com/careers/test",
        "required_skills": ["Kubernetes", "Golang", "Distributed Systems"],
        "match_score": 0.0,
        "eligible": False,
        "tailored_cover_letter": "",
        "custom_qa": {},
        "application_status": "initiated",
        "receipt": {},
        "error_message": ""
    }

    result = auto_apply_agent_graph.invoke(initial_state)

    assert result["eligible"] is False
    assert result["application_status"] == "ineligible_skipped"
    assert result.get("receipt") == {}
