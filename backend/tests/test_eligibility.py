
from types import SimpleNamespace

from app.services.eligibility import check_eligibility


def test_eligible_student():
    student = SimpleNamespace(
        cgpa=8.5,
        branch="CSE",
        graduation_year=2027,
        skills="Python, Java, SQL"
    )

    job = SimpleNamespace(
        minimum_cgpa=6.0,
        eligible_branches="CSE, IT",
        graduation_year=2027,
        required_skills="Java, SQL"
    )

    result = check_eligibility(student, job)

    assert result["eligible"] is True
    assert result["skill_match_percentage"] == 100


def test_ineligible_student():
    student = SimpleNamespace(
        cgpa=5.0,
        branch="ECE",
        graduation_year=2026,
        skills="HTML, CSS"
    )

    job = SimpleNamespace(
        minimum_cgpa=7.0,
        eligible_branches="CSE, IT",
        graduation_year=2027,
        required_skills="Java, SQL"
    )

    result = check_eligibility(student, job)

    assert result["eligible"] is False
    assert len(result["reasons"]) >= 3