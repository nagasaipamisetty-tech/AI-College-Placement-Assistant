
import json
import re
import pandas as pd

from sqlalchemy.orm import Session

from app.models import Student


def normalize_header(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_column(columns, candidates):
    normalized = {
        normalize_header(column): column
        for column in columns
    }

    for candidate in candidates:
        key = normalize_header(candidate)
        if key in normalized:
            return normalized[key]

    return None


def import_students(file, db: Session):
    frame = pd.read_csv(file).fillna("")
    frame.columns = [str(c).strip() for c in frame.columns]

    roll_col = find_column(
        frame.columns,
        ["roll_number", "roll no", "rollno", "student_id", "student roll no", "student_roll_no"]
    )
    name_col = find_column(
        frame.columns, ["name", "student_name", "full_name", "student full name", "student_full_name"]
    )
    email_col = find_column(
        frame.columns, ["email", "email_id", "email_address", "e-mail id", "e_mail_id", "mail id"]
    )
    branch_col = find_column(
        frame.columns, ["branch", "department", "course", "branch_code"]
    )
    cgpa_col = find_column(
        frame.columns, ["cgpa", "gpa", "grade_point", "b.tech cgpa", "btech cgpa", "btech_cgpa", "b tech cgpa"]
    )
    year_col = find_column(
        frame.columns,
        ["graduation_year", "passing_year", "year_of_passing", "year of pass", "year_of_pass", "yop"]
    )
    skills_col = find_column(
        frame.columns, ["skills", "technical_skills", "technical skills", "tech_skills"]
    )

    if not roll_col or not name_col or not email_col:
        raise ValueError(
            "CSV must include roll number, name and email columns."
        )

    added = 0
    updated = 0
    skipped = 0
    errors = []

    for index, row in frame.iterrows():
        roll = str(row[roll_col]).strip()
        name = str(row[name_col]).strip()
        email = str(row[email_col]).strip().lower()

        if not roll or not name or "@" not in email:
            skipped += 1
            errors.append(f"Row {index + 2}: missing or invalid data")
            continue

        existing = db.query(Student).filter(
            Student.roll_number == roll
        ).first()

        email_owner = db.query(Student).filter(
            Student.email == email
        ).first()

        if email_owner and (
            existing is None or email_owner.id != existing.id
        ):
            skipped += 1
            errors.append(
                f"Row {index + 2}: email already belongs to another student"
            )
            continue

        cgpa = None
        year = None

        try:
            if cgpa_col and str(row[cgpa_col]).strip():
                cgpa = float(row[cgpa_col])
                if not 0 <= cgpa <= 10:
                    raise ValueError()
        except (ValueError, TypeError):
            skipped += 1
            errors.append(f"Row {index + 2}: invalid CGPA")
            continue

        try:
            if year_col and str(row[year_col]).strip():
                year = int(float(row[year_col]))
        except (ValueError, TypeError):
            skipped += 1
            errors.append(f"Row {index + 2}: invalid graduation year")
            continue

        values = {
            "name": name,
            "email": email,
            "branch": str(row[branch_col]).strip() if branch_col else "",
            "cgpa": cgpa,
            "graduation_year": year,
            "skills": str(row[skills_col]).strip() if skills_col else "",
            "raw_data": json.dumps(
                {str(k): str(v) for k, v in row.to_dict().items()}
            ),
            "approved_for_registration": True
        }

        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            updated += 1
        else:
            db.add(Student(roll_number=roll, **values))
            added += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "total_rows": len(frame),
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:50]
    }