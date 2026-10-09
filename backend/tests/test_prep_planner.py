from types import SimpleNamespace
from app.services.matching import calculate_job_match, rank_jobs_for_student
from app.services.prep_planner import generate_interview_prep_plan


def test_matching_and_ranking():
    student = SimpleNamespace(
        id=1,
        name="Test Student",
        email="test@college.edu",
        roll_number="23471A0501",
        cgpa=8.5,
        branch="CSE",
        graduation_year=2027,
        skills="Python:Advanced|Java:Intermediate|SQL:Advanced"
    )

    job1 = SimpleNamespace(
        id=101,
        title="Software Engineer",
        company_name="Google",
        description="Backend role",
        required_skills="Python, SQL",
        minimum_cgpa=7.0,
        eligible_branches="CSE, IT",
        graduation_year=2027,
        status="approved"
    )

    job2 = SimpleNamespace(
        id=102,
        title="Cloud Engineer",
        company_name="AWS",
        description="DevOps role",
        required_skills="Docker, AWS, Linux",
        minimum_cgpa=6.5,
        eligible_branches="CSE, IT",
        graduation_year=2027,
        status="approved"
    )

    ranked = rank_jobs_for_student(student, [job1, job2])
    assert len(ranked) == 2
    assert ranked[0]["job_id"] == 101
    assert ranked[0]["fit_score"] > ranked[1]["fit_score"]
    assert ranked[0]["tier"] == "Strong Match"


def test_prep_plan_generation():
    student = SimpleNamespace(
        id=1,
        name="Test Student",
        email="test@college.edu",
        roll_number="23471A0501",
        cgpa=8.0,
        branch="CSE",
        graduation_year=2027,
        skills="Python, Java"
    )

    job = SimpleNamespace(
        id=101,
        title="Data Engineer",
        company_name="Amazon",
        description="Data pipeline engineering",
        required_skills="Python, SQL, AWS",
        minimum_cgpa=7.0,
        eligible_branches="CSE, IT",
        graduation_year=2027,
        status="approved"
    )

    plan = generate_interview_prep_plan(student, job)
    assert plan["job_id"] == 101
    assert "SQL" in [g["skill"] for g in plan["gap_breakdown"]] or "Sql" in [g["skill"] for g in plan["gap_breakdown"]]
    assert len(plan["daily_roadmap"]) == 30
    assert plan["total_days"] == 30
    assert len(plan["mock_questions"]["technical_coding"]) >= 3
    assert len(plan["mock_questions"]["behavioral_star"]) >= 2

    # Test custom target days (e.g. 7-day fast-track or 14-day sprint)
    plan_7d = generate_interview_prep_plan(student, job, target_days=7)
    assert len(plan_7d["daily_roadmap"]) == 7
    assert plan_7d["total_days"] == 7

    plan_14d = generate_interview_prep_plan(student, job, target_days=14)
    assert len(plan_14d["daily_roadmap"]) == 14
    assert plan_14d["total_days"] == 14


def test_autonomous_agent():
    from app.agent.agent_core import AutonomousPlacementAgent
    agent = AutonomousPlacementAgent()

    student = SimpleNamespace(
        id=1,
        name="Test Student",
        email="test@college.edu",
        roll_number="23471A0501",
        cgpa=8.0,
        branch="CSE",
        graduation_year=2027,
        skills="Python, SQL"
    )

    job = SimpleNamespace(
        id=101,
        title="Frontend Engineer",
        company_name="Google",
        description="React and web frontend",
        required_skills="React, JavaScript, HTML/CSS",
        minimum_cgpa=7.0,
        eligible_branches="CSE, IT",
        graduation_year=2027,
        status="approved"
    )

    # Test full plan
    plan = agent.generate_plan(student, job, duration_days=7)
    assert plan["job_id"] == 101
    assert len(plan["daily_roadmap"]) == 7
    assert "react" in [s.lower() for s in plan["missing_skills"]]

    # Test interactive 3-day query
    chat_3day = agent.chat_interact(student, job, "give me a 3 day crash course plan")
    assert chat_3day["type"] == "plan"
    assert len(chat_3day["data"]["daily_roadmap"]) == 3

    # Test mock questions query
    chat_mock = agent.chat_interact(student, job, "generate mock interview questions")
    assert chat_mock["type"] == "questions"
    assert "technical_coding" in chat_mock["data"]

