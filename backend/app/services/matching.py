from app.services.eligibility import check_eligibility, parse_skills


def calculate_job_match(student, job):
    eligibility = check_eligibility(student, job)

    required_skills = parse_skills(job.required_skills)
    student_skills = parse_skills(student.skills)

    matched_skills = sorted(required_skills & student_skills)
    missing_skills = sorted(required_skills - student_skills)

    skill_score = eligibility.get("skill_match_percentage", 0)

    # CGPA bonus calculation (up to 20 pts)
    cgpa_diff = max(0.0, (student.cgpa or 0) - job.minimum_cgpa)
    cgpa_score = min(20, round(cgpa_diff * 10))

    # Branch match score (10 pts if branch matched)
    branches = [
        b.strip().lower()
        for b in (job.eligible_branches or "").split(",")
        if b.strip()
    ]
    branch_score = 10 if not branches or (student.branch or "").strip().lower() in branches else 0

    if not eligibility["eligible"]:
        # If ineligible by hard criteria (CGPA/branch)
        if (student.cgpa or 0) < job.minimum_cgpa or (branches and (student.branch or "").strip().lower() not in branches):
            fit_score = max(0, round(skill_score * 0.4))
            tier = "Ineligible"
        else:
            fit_score = max(20, round(skill_score * 0.7 + cgpa_score + branch_score))
            tier = "Needs Skill Prep"
    else:
        fit_score = min(100, round(skill_score * 0.7 + cgpa_score + branch_score))
        if fit_score >= 85:
            tier = "Strong Match"
        elif fit_score >= 65:
            tier = "Good Match"
        else:
            tier = "Moderate Match"

    return {
        "job_id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "description": job.description,
        "required_skills": job.required_skills,
        "minimum_cgpa": job.minimum_cgpa,
        "eligible_branches": job.eligible_branches,
        "graduation_year": job.graduation_year,
        "eligible": eligibility["eligible"],
        "eligibility_reasons": eligibility["reasons"],
        "skill_match_percentage": skill_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "fit_score": fit_score,
        "tier": tier
    }


def rank_jobs_for_student(student, jobs):
    ranked = []
    for job in jobs:
        if job.status == "approved":
            match_data = calculate_job_match(student, job)
            ranked.append(match_data)

    # Sort descending by eligible flag, then fit_score, then skill_match_percentage
    ranked.sort(key=lambda x: (x["eligible"], x["fit_score"], x["skill_match_percentage"]), reverse=True)
    return ranked
