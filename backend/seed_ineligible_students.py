import os
import sys
import libsql_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import User, Student
from app.core.security import hash_password
from app.core.config import settings

INELIGIBLE_STUDENTS = [
    {
        "name": "Arjun Kumar (Low CGPA)",
        "email": "ineligible.lowcgpa1@college.edu",
        "roll_number": "23CS901",
        "branch": "CSE",
        "cgpa": 5.40,
        "graduation_year": 2027,
        "skills": "C:Beginner|HTML/CSS:Beginner|Basic Python:Beginner",
        "reason": "CGPA (5.40) is below company minimum cutoffs (6.5 - 7.5)"
    },
    {
        "name": "Kavya Sharma (Low CGPA)",
        "email": "ineligible.lowcgpa2@college.edu",
        "roll_number": "23EC902",
        "branch": "ECE",
        "cgpa": 5.75,
        "graduation_year": 2027,
        "skills": "C:Beginner|Basic Electronics:Intermediate",
        "reason": "CGPA (5.75) is below company minimum cutoffs (6.5 - 7.5)"
    },
    {
        "name": "Rahul Verma (Civil Non-Tech)",
        "email": "ineligible.branch1@college.edu",
        "roll_number": "23CE903",
        "branch": "CIVIL",
        "cgpa": 8.20,
        "graduation_year": 2027,
        "skills": "AutoCAD:Advanced|Surveying:Advanced|Concrete Technology:Advanced",
        "reason": "High CGPA (8.20) but Branch (CIVIL) is not in eligible branches list for Tech SDE roles"
    },
    {
        "name": "Priya Patel (Mech Non-Tech)",
        "email": "ineligible.branch2@college.edu",
        "roll_number": "23ME904",
        "branch": "MECH",
        "cgpa": 7.90,
        "graduation_year": 2027,
        "skills": "SolidWorks:Advanced|Thermodynamics:Advanced|MATLAB:Intermediate",
        "reason": "High CGPA (7.90) but Branch (MECH) and skills do not match SDE software requirements"
    },
    {
        "name": "Suresh Reddy (Missing Skills)",
        "email": "ineligible.noskills@college.edu",
        "roll_number": "23CS905",
        "branch": "CSE",
        "cgpa": 7.10,
        "graduation_year": 2027,
        "skills": "MS Office:Advanced|HTML/CSS:Beginner|English Communication:Advanced",
        "reason": "Eligible Branch (CSE) and CGPA (7.10), but 0% Skill Match for core SDE requirements"
    }
]


def seed_ineligible_accounts():
    print("==================================================")
    print("[+] Seeding 5 Ineligible Student Accounts Locally...")
    print("==================================================")

    db = SessionLocal()
    password_hash = hash_password("Student@123")

    for s_data in INELIGIBLE_STUDENTS:
        # 1. Ensure User Account
        user = db.query(User).filter(User.email == s_data["email"]).first()
        if not user:
            user = User(
                name=s_data["name"],
                email=s_data["email"],
                password_hash=password_hash,
                role="student",
                is_active=True
            )
            db.add(user)
            print(f"  - Created user account: {s_data['email']}")
        else:
            print(f"  - User account exists: {s_data['email']}")

        # 2. Ensure Student Record
        student = db.query(Student).filter(Student.email == s_data["email"]).first()
        if not student:
            student = Student(
                name=s_data["name"],
                email=s_data["email"],
                roll_number=s_data["roll_number"],
                branch=s_data["branch"],
                cgpa=s_data["cgpa"],
                graduation_year=s_data["graduation_year"],
                skills=s_data["skills"],
                approved_for_registration=True
            )
            db.add(student)
            print(f"  - Created student record: {s_data['name']} (CGPA: {s_data['cgpa']}, Branch: {s_data['branch']})")
        else:
            student.cgpa = s_data["cgpa"]
            student.branch = s_data["branch"]
            student.skills = s_data["skills"]
            print(f"  - Updated student record: {s_data['name']}")

    db.commit()
    db.close()
    print("\n[SUCCESS] Local SQLite database updated successfully!")

    # 3. Sync with Turso Cloud Database
    url = settings.turso_database_url
    token = settings.turso_auth_token

    if url and token:
        print("\n==================================================")
        print("[+] Synchronizing 5 Ineligible Accounts to Turso Cloud DB...")
        print("==================================================")
        try:
            client = libsql_client.create_client_sync(url=url, auth_token=token)
            for s in INELIGIBLE_STUDENTS:
                # Upsert user
                client.execute(
                    """
                    INSERT INTO users (name, email, password_hash, role, is_active)
                    VALUES (?, ?, ?, 'student', 1)
                    ON CONFLICT(email) DO UPDATE SET
                        name=excluded.name,
                        password_hash=excluded.password_hash;
                    """,
                    [s["name"], s["email"], password_hash]
                )

                # Upsert student
                client.execute(
                    """
                    INSERT INTO students (roll_number, name, email, branch, graduation_year, cgpa, skills, approved_for_registration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(email) DO UPDATE SET
                        roll_number=excluded.roll_number,
                        name=excluded.name,
                        branch=excluded.branch,
                        graduation_year=excluded.graduation_year,
                        cgpa=excluded.cgpa,
                        skills=excluded.skills;
                    """,
                    [s["roll_number"], s["name"], s["email"], s["branch"], s["graduation_year"], s["cgpa"], s["skills"]]
                )
                print(f"  - Synced to Turso: {s['email']}")

            print("[SUCCESS] Turso Cloud Database successfully synced!")
        except Exception as e:
            print(f"[!] Turso sync error: {e}")


if __name__ == "__main__":
    seed_ineligible_accounts()
