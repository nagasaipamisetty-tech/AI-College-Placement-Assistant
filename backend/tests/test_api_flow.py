from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_auth_and_admin_flow():
    # Login as admin
    res = client.post("/api/auth/login", json={"email": "admin@college.edu", "password": "Admin@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get /me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["role"] == "admin"

    # Admin summary
    summary_res = client.get("/api/admin/summary", headers=headers)
    assert summary_res.status_code == 200
    data = summary_res.json()
    assert data["students"] > 0
    assert data["jobs_approved"] > 0


def test_student_flow():
    # Login as student
    res = client.post("/api/auth/login", json={"email": "student@college.edu", "password": "Student@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Student profile
    prof_res = client.get("/api/students/me", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["roll_number"] == "23471A0500"

    # Update Student Profile social & coding handles
    update_prof = client.put("/api/students/me", headers=headers, json={
        "phone": "+91 9876543210",
        "linkedin_url": "https://linkedin.com/in/student",
        "github_url": "https://github.com/student",
        "hackerrank_url": "https://hackerrank.com/student",
        "leetcode_url": "https://leetcode.com/student",
        "portfolio_url": "https://student.dev",
        "bio": "Aspiring Software Engineer & AI Researcher"
    })
    assert update_prof.status_code == 200
    updated_data = update_prof.json()
    assert updated_data["linkedin_url"] == "https://linkedin.com/in/student"
    assert updated_data["github_url"] == "https://github.com/student"
    assert updated_data["hackerrank_url"] == "https://hackerrank.com/student"

    # List approved jobs
    jobs_res = client.get("/api/jobs/", headers=headers)
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()
    assert len(jobs) > 0

    # Find Google SDE job for which student is eligible
    sde_jobs = [j for j in jobs if "Google" in j.get("company_name", "") or "Software" in j.get("title", "")]
    assert len(sde_jobs) > 0
    job = sde_jobs[0]

    # Check eligibility
    elig_res = client.get(f"/api/students/me/eligibility/{job['id']}", headers=headers)
    assert elig_res.status_code == 200
    elig_data = elig_res.json()
    assert elig_data["eligible"] is True
    assert elig_data["skill_match_percentage"] == 100

    # Apply for job (or already applied)
    apply_res = client.post("/api/applications/", json={"job_id": job["id"]}, headers=headers)
    assert apply_res.status_code in [201, 409]

    # Check my applications
    apps_res = client.get("/api/applications/mine", headers=headers)
    assert apps_res.status_code == 200
    assert len(apps_res.json()) >= 1


def test_training_flow():
    res = client.post("/api/auth/login", json={"email": "student@college.edu", "password": "Student@123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List training sessions
    train_res = client.get("/api/training/", headers=headers)
    assert train_res.status_code == 200
    sessions = train_res.json()
    assert len(sessions) > 0

    # Enroll in first session
    first_id = sessions[0]["id"]
    enroll_res = client.post(f"/api/training/{first_id}/enroll", headers=headers)
    assert enroll_res.status_code in [200, 409]


def test_operator_flow():
    res = client.post("/api/auth/login", json={"email": "operator@college.edu", "password": "Operator@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    stats_res = client.get("/api/operator/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_students" in stats
    assert "approved_jobs" in stats


def test_matched_jobs_and_prep_plan_api():
    # Login as student
    res = client.post("/api/auth/login", json={"email": "student@college.edu", "password": "Student@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get matched jobs ranked
    matches_res = client.get("/api/students/me/matched-jobs", headers=headers)
    assert matches_res.status_code == 200
    matches = matches_res.json()
    assert len(matches) > 0
    first_job_id = matches[0]["job_id"]

    # 2. Generate prep plan (default 30 days)
    plan_res = client.post(f"/api/students/me/prep-plan/{first_job_id}?days=30", headers=headers)
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert "daily_roadmap" in plan_data
    assert "mock_questions" in plan_data
    assert len(plan_data["daily_roadmap"]) == 30
    assert plan_data["total_days"] == 30

    # 3. Retrieve existing plan
    get_plan_res = client.get(f"/api/students/me/prep-plan/{first_job_id}", headers=headers)
    assert get_plan_res.status_code == 200
    assert get_plan_res.json()["job_id"] == first_job_id

    # 4. List saved plans
    list_plans_res = client.get("/api/students/me/prep-plans", headers=headers)
    assert list_plans_res.status_code == 200
    assert len(list_plans_res.json()) >= 1


def test_admin_skill_search_and_prep_plan():
    # Login as admin
    res = client.post("/api/auth/login", json={"email": "admin@college.edu", "password": "Admin@123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Search students by skill
    skill_res = client.get("/api/students/?skill=Python", headers=headers)
    assert skill_res.status_code == 200
    students_with_python = skill_res.json()
    assert len(students_with_python) > 0

    # 2. Search students by branch and CGPA cutoff
    cgpa_res = client.get("/api/students/?branch=CSE&min_cgpa=7.0", headers=headers)
    assert cgpa_res.status_code == 200
    cse_students = cgpa_res.json()
    assert len(cse_students) > 0

    # 3. Admin view student's matched opportunities
    first_student_id = cse_students[0]["id"]
    match_res = client.get(f"/api/students/{first_student_id}/matched-jobs", headers=headers)
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert "matches" in match_data
    assert "student" in match_data

    # 4. Admin generate prep plan for student
    if len(match_data["matches"]) > 0:
        job_id = match_data["matches"][0]["job_id"]
        admin_plan_res = client.post(f"/api/students/{first_student_id}/prep-plan/{job_id}", headers=headers)
        assert admin_plan_res.status_code == 200
        assert "daily_roadmap" in admin_plan_res.json()


def test_admin_and_operator_add_edit_and_drive_override():
    # Login as operator
    op_login = client.post("/api/auth/login", json={"email": "operator@college.edu", "password": "Operator@123"})
    assert op_login.status_code == 200
    op_token = op_login.json()["access_token"]
    op_headers = {"Authorization": f"Bearer {op_token}"}

    # 1. Operator creates a student
    create_res = client.post("/api/students/", headers=op_headers, json={
        "roll_number": "TESTOP001",
        "name": "Operator Test Student",
        "email": "testop@college.edu",
        "branch": "ECE",
        "graduation_year": 2026,
        "cgpa": 5.8,  # Lower than typical 7.5+ cutoff
        "skills": "C, Embedded Systems"
    })
    assert create_res.status_code == 201
    created_student = create_res.json()
    student_id = created_student["id"]

    # 2. Operator updates student details
    edit_res = client.put(f"/api/students/{student_id}", headers=op_headers, json={
        "name": "Operator Test Student Updated",
        "cgpa": 6.2,
        "skills": "C, Embedded Systems, RTOS"
    })
    assert edit_res.status_code == 200
    assert edit_res.json()["name"] == "Operator Test Student Updated"
    assert edit_res.json()["cgpa"] == 6.2

    # 3. Get any approved job with higher CGPA cutoff (e.g. 7.5+)
    jobs_res = client.get("/api/jobs/", headers=op_headers)
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()
    assert len(jobs) > 0
    target_job = jobs[0]

    # 4. Operator overrides eligibility to enroll the student directly into the drive
    override_res = client.post("/api/applications/override-apply", headers=op_headers, json={
        "student_id": student_id,
        "job_id": target_job["id"],
        "status": "applied"
    })
    assert override_res.status_code == 201
    assert override_res.json()["overridden"] is True

    # 5. Clean up - delete the test student
    del_res = client.delete(f"/api/students/{student_id}", headers=op_headers)
    assert del_res.status_code == 200



