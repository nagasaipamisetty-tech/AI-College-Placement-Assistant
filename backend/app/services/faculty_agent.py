import io
import csv
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import Student, Job
from app.services.eligibility import check_eligibility, parse_skills


def evaluate_students_for_requirements(
    db: Session,
    minimum_cgpa: float = 0.0,
    eligible_branches: Optional[List[str]] = None,
    required_skills: Optional[List[str]] = None,
    graduation_year: Optional[int] = None,
    min_skill_match_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Autonomous Faculty Agent Engine:
    Evaluates all students in the database against target company requirements.
    """
    all_students = db.query(Student).all()

    req_skills = [s.strip().lower() for s in (required_skills or []) if s.strip()]
    allowed_branches = [b.strip().lower() for b in (eligible_branches or []) if b.strip()]

    eligible_list = []
    ineligible_list = []
    branch_distribution = {}
    skill_gap_frequency = {}

    total_cgpa_eligible = 0.0

    for student in all_students:
        s_cgpa = student.cgpa or 0.0
        s_branch = (student.branch or "").strip()
        s_branch_lower = s_branch.lower()
        s_grad_year = student.graduation_year

        # Parse Student Skills
        s_skills_raw = parse_skills(student.skills)
        s_skills_set = {s.lower() for s in s_skills_raw}

        # Calculate Skill Match
        if req_skills:
            matched_skills = [s for s in req_skills if any(s in acquired or acquired in s for acquired in s_skills_set)]
            missing_skills = [s for s in req_skills if s not in matched_skills]
            match_pct = round(100.0 * len(matched_skills) / len(req_skills), 1)
        else:
            matched_skills = []
            missing_skills = []
            match_pct = 100.0

        # Eligibility Checks
        reasons = []
        is_eligible = True

        if s_cgpa < minimum_cgpa:
            is_eligible = False
            reasons.append(f"CGPA {s_cgpa:.2f} below minimum cutoff of {minimum_cgpa:.2f}")

        if allowed_branches:
            if not any(allowed in s_branch_lower for allowed in allowed_branches):
                is_eligible = False
                reasons.append(f"Branch '{s_branch}' not in eligible list ({', '.join(eligible_branches)})")

        if graduation_year and s_grad_year:
            if s_grad_year != graduation_year:
                is_eligible = False
                reasons.append(f"Graduation year {s_grad_year} does not match required {graduation_year}")

        if match_pct < min_skill_match_pct:
            is_eligible = False
            reasons.append(f"Skill match {match_pct}% is below minimum required {min_skill_match_pct}%")

        # Track skill gaps across students
        for gap in missing_skills:
            gap_cap = gap.title()
            skill_gap_frequency[gap_cap] = skill_gap_frequency.get(gap_cap, 0) + 1

        record = {
            "student_id": student.id,
            "roll_number": student.roll_number,
            "name": student.name,
            "email": student.email,
            "branch": s_branch,
            "cgpa": s_cgpa,
            "graduation_year": s_grad_year,
            "skill_match_percentage": match_pct,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skills": student.skills,
            "eligible": is_eligible,
            "reasons": reasons,
            "readiness_tier": (
                "Tier 1: Placement Ready" if match_pct >= 75 and s_cgpa >= minimum_cgpa + 0.5
                else "Tier 2: Eligible with Minor Gaps" if is_eligible
                else "Tier 3: Ineligible"
            )
        }

        if is_eligible:
            eligible_list.append(record)
            total_cgpa_eligible += s_cgpa
            branch_distribution[s_branch] = branch_distribution.get(s_branch, 0) + 1
        else:
            ineligible_list.append(record)

    # Sort eligible students by CGPA desc, then match_pct desc
    eligible_list.sort(key=lambda s: (s["cgpa"], s["skill_match_percentage"]), reverse=True)

    avg_eligible_cgpa = round(total_cgpa_eligible / len(eligible_list), 2) if eligible_list else 0.0

    # Top skill gaps across candidate pool
    sorted_skill_gaps = sorted(skill_gap_frequency.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "summary": {
            "total_evaluated": len(all_students),
            "eligible_count": len(eligible_list),
            "ineligible_count": len(ineligible_list),
            "eligibility_rate_pct": round(100.0 * len(eligible_list) / len(all_students), 1) if all_students else 0.0,
            "average_eligible_cgpa": avg_eligible_cgpa,
            "branch_distribution": branch_distribution,
            "top_skill_gaps": [{"skill": s, "affected_students": count} for s, count in sorted_skill_gaps]
        },
        "eligible_students": eligible_list,
        "ineligible_students": ineligible_list
    }


def generate_shortlist_csv(eligible_students: List[Dict[str, Any]], company_name: str, job_title: str) -> str:
    """
    Generates a formal CSV shortlist export ready for campus recruiters.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header rows
    writer.writerow(["COLLEGE PLACEMENT CELL - OFFICIAL CANDIDATE SHORTLIST"])
    writer.writerow(["Company:", company_name, "Role:", job_title])
    writer.writerow(["Total Candidates Shortlisted:", len(eligible_students)])
    writer.writerow([])
    writer.writerow([
        "S.No",
        "Roll Number",
        "Student Name",
        "Email",
        "Department / Branch",
        "CGPA",
        "Skill Match %",
        "Matched Skills",
        "Identified Skill Gaps",
        "Readiness Tier"
    ])

    for idx, s in enumerate(eligible_students, start=1):
        writer.writerow([
            idx,
            s.get("roll_number", ""),
            s.get("name", ""),
            s.get("email", ""),
            s.get("branch", ""),
            s.get("cgpa", 0.0),
            f"{s.get('skill_match_percentage', 0)}%",
            ", ".join(s.get("matched_skills", [])),
            ", ".join(s.get("missing_skills", [])),
            s.get("readiness_tier", "")
        ])

    return output.getvalue()
