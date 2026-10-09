import re


def parse_skills(raw_skills: str) -> set[str]:
    if not raw_skills:
        return set()
    # Split by comma or pipe
    tokens = re.split(r"[,|]", str(raw_skills))
    cleaned = set()
    for token in tokens:
        # Strip level tag like "Python:Advanced" -> "python"
        base_skill = token.split(":")[0].strip().lower()
        if base_skill:
            cleaned.add(base_skill)
    return cleaned


def check_eligibility(student, job):
    reasons = []

    s_cgpa = student.cgpa or 0.0
    if s_cgpa < job.minimum_cgpa:
        reasons.append(
            f"CGPA Deficiency: Your current CGPA ({s_cgpa:.2f}) does not meet the minimum cutoff of {job.minimum_cgpa:.2f}."
        )

    branches = [
        value.strip().lower()
        for value in (job.eligible_branches or "").split(",")
        if value.strip()
    ]

    s_branch = (student.branch or "").strip()
    if branches and s_branch.lower() not in branches:
        reasons.append(
            f"Branch Ineligibility: Your department/branch ('{s_branch}') is not eligible for this role. Allowed branches: {job.eligible_branches}."
        )

    if (
        job.graduation_year is not None
        and student.graduation_year != job.graduation_year
    ):
        reasons.append(
            f"Batch Year Mismatch: Your graduation batch ({student.graduation_year or 'Unspecified'}) does not match the target hiring batch of {job.graduation_year}."
        )

    required = parse_skills(job.required_skills)
    student_skills = parse_skills(student.skills)

    missing = sorted(required - student_skills)
    matched_set = required & student_skills

    if missing:
        reasons.append(
            f"Missing Technical Skills: You are missing {len(missing)} required core skill(s): {', '.join(missing)}."
        )

    matched = len(matched_set)
    skill_score = round(100 * matched / len(required)) if required else 100

    # Hard eligibility is determined by academic cutoffs (CGPA, Branch, Batch)
    # A candidate is eligible to apply if they meet the hard criteria, even with minor skill gaps
    hard_criteria_met = (
        s_cgpa >= job.minimum_cgpa
        and (not branches or s_branch.lower() in branches)
        and (job.graduation_year is None or student.graduation_year == job.graduation_year)
    )

    return {
        "eligible": hard_criteria_met,
        "reasons": reasons,
        "skill_match_percentage": skill_score,
        "matched_skills": sorted(list(matched_set)),
        "missing_skills": missing
    }