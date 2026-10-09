import pytest
from app.services.latex_resume import build_latex_resume_code, categorize_skills, generate_tailored_projects


def test_build_latex_resume_code():
    tex = build_latex_resume_code(
        name="MOHAMMAD RAFI YARLAGADDA",
        email="yarlagaddamohammadrafi2005@mail.example",
        roll_number="23CS001",
        branch="CSE",
        cgpa=9.60,
        grad_year=2027,
        job_title="Software Development Engineer - Distributed Systems",
        company_name="Uber",
        required_skills=["Python", "Docker", "FastAPI", "SQL"],
        student_skills=["C", "Java", "Python", "SQL", "DBMS", "AWS", "REST APIs", "Linux"]
    )

    assert r"\documentclass[a4paper,10pt]{article}" in tex
    assert "MOHAMMAD RAFI YARLAGADDA" in tex
    assert "Uber" in tex
    assert "Software Development Engineer - Distributed Systems" in tex
    assert "9.60" in tex
    assert r"\section{\color{BlueViolet} Objective}" in tex
    assert r"\section{\color{BlueViolet} Skills Summary}" in tex
    assert r"\section{\color{BlueViolet} Projects}" in tex
    assert r"\end{document}" in tex


def test_categorize_skills_prioritization():
    categories = categorize_skills(
        student_skills=["Java", "C++", "Python", "Docker", "SQL"],
        target_skills=["Python", "SQL"]
    )

    assert "Python" in categories["Languages"]
    assert "Languages" in categories
    assert "Tools/Platforms" in categories
