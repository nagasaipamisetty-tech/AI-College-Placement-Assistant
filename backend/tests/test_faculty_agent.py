import pytest
from app.db import SessionLocal
from app.services.faculty_agent import evaluate_students_for_requirements, generate_shortlist_csv


def test_faculty_agent_evaluation():
    db = SessionLocal()
    try:
        res = evaluate_students_for_requirements(
            db=db,
            minimum_cgpa=7.0,
            eligible_branches=["CSE", "CSE-AIML", "IT"],
            required_skills=["Python", "SQL"],
            min_skill_match_pct=30.0
        )

        assert "summary" in res
        assert res["summary"]["total_evaluated"] >= 50
        assert res["summary"]["eligible_count"] > 0
        assert "branch_distribution" in res["summary"]

        csv_text = generate_shortlist_csv(res["eligible_students"], "Google", "Software Engineer")
        assert "COLLEGE PLACEMENT CELL" in csv_text
        assert "Google" in csv_text
    finally:
        db.close()
