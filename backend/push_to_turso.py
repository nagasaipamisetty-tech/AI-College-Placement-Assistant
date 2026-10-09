import os
import sys
import pandas as pd
import libsql_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import hash_password


def push_schema_and_data_to_turso():
    url = settings.turso_database_url
    token = settings.turso_auth_token

    if not url or not token:
        print("[!] Error: TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set in .env")
        return

    print("==================================================")
    print(f"Connecting to Turso Cloud DB: {url}")
    print("==================================================")

    client = libsql_client.create_client_sync(url=url, auth_token=token)

    try:
        # 1. Create Tables
        print("\n[+] Creating Turso Database Tables...")
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(150) DEFAULT '',
                email VARCHAR(255) UNIQUE,
                password_hash VARCHAR(255),
                role VARCHAR(30) DEFAULT 'student',
                is_active BOOLEAN DEFAULT 1
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number VARCHAR(50) UNIQUE,
                name VARCHAR(150),
                email VARCHAR(255) UNIQUE,
                branch VARCHAR(100) DEFAULT '',
                graduation_year INTEGER,
                cgpa REAL,
                skills TEXT DEFAULT '',
                raw_data TEXT DEFAULT '{}',
                approved_for_registration BOOLEAN DEFAULT 1
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200),
                company_name VARCHAR(200),
                description TEXT DEFAULT '',
                required_skills TEXT DEFAULT '',
                minimum_cgpa REAL DEFAULT 0.0,
                eligible_branches TEXT DEFAULT '',
                graduation_year INTEGER,
                status VARCHAR(30) DEFAULT 'pending',
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                job_id INTEGER,
                status VARCHAR(30) DEFAULT 'applied',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, job_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200),
                description TEXT DEFAULT '',
                trainer VARCHAR(150) DEFAULT '',
                scheduled_at TIMESTAMP,
                capacity INTEGER DEFAULT 50,
                created_by INTEGER
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                training_id INTEGER,
                status VARCHAR(30) DEFAULT 'enrolled',
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, training_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS interview_prep_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                job_id INTEGER,
                skill_gaps TEXT DEFAULT '',
                skill_match_percentage REAL DEFAULT 0.0,
                plan_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, job_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS auto_apply_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                confirmation_id VARCHAR(50) UNIQUE,
                job_id VARCHAR(100),
                job_title VARCHAR(200),
                company_name VARCHAR(200),
                portal_url TEXT DEFAULT '',
                match_score REAL DEFAULT 0.0,
                status VARCHAR(50) DEFAULT 'SUBMITTED',
                tailored_cover_letter TEXT DEFAULT '',
                custom_qa_json TEXT DEFAULT '{}',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]

        for stmt in tables:
            client.execute(stmt)
        print("  - All 8 tables created successfully on Turso!")

        # 2. Seed Users
        print("\n[+] Seeding Default Users into Turso...")
        users = [
            ("Placement Administrator", "admin@college.edu", hash_password("Admin@123"), "admin", 1),
            ("Placement Operator", "operator@college.edu", hash_password("Operator@123"), "operator", 1),
            ("Technical Trainer", "trainer@college.edu", hash_password("Trainer@123"), "training", 1),
            ("Google Campus Recruiter", "recruiter@google.com", hash_password("Company@123"), "company", 1),
            ("Demo Student", "student@college.edu", hash_password("Student@123"), "student", 1),
        ]

        for u in users:
            client.execute(
                "INSERT OR IGNORE INTO users (name, email, password_hash, role, is_active) VALUES (?, ?, ?, ?, ?);",
                list(u)
            )
        print("  - Seeded 5 system user accounts.")

        # 3. Seed Demo Student
        client.execute(
            """
            INSERT OR IGNORE INTO students 
            (roll_number, name, email, branch, graduation_year, cgpa, skills, approved_for_registration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            ["23471A0500", "Demo Student", "student@college.edu", "CSE", 2027, 8.5, "Python, Java, SQL, React, Docker, Data Structures", 1]
        )

        # 4. Ingest CSV data
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "students_data.csv")
        if os.path.exists(csv_path):
            print(f"\n[+] Ingesting Student CSV into Turso: {os.path.normpath(csv_path)}")
            df = pd.read_csv(csv_path).fillna("")
            inserted = 0
            for _, row in df.iterrows():
                roll = str(row.get("Student Roll No") or row.get("roll_number") or "").strip()
                name = str(row.get("Student Full Name") or row.get("name") or "").strip()
                email = str(row.get("E-Mail id") or row.get("email") or "").strip().lower()
                branch = str(row.get("Branch") or "").strip()
                cgpa_str = str(row.get("B.Tech CGPA") or row.get("cgpa") or "0").strip()
                year_str = str(row.get("Year of Pass") or row.get("graduation_year") or "2027").strip()
                skills = str(row.get("Technical Skills") or row.get("skills") or "").strip()

                if not roll or not name or "@" not in email:
                    continue

                try:
                    cgpa = float(cgpa_str) if cgpa_str else None
                except ValueError:
                    cgpa = None

                try:
                    year = int(float(year_str)) if year_str else 2027
                except ValueError:
                    year = 2027

                client.execute(
                    """
                    INSERT OR IGNORE INTO students 
                    (roll_number, name, email, branch, graduation_year, cgpa, skills, approved_for_registration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1);
                    """,
                    [roll, name, email, branch, year, cgpa, skills]
                )
                inserted += 1
            print(f"  - Ingested {inserted} student records to Turso!")

        # 5. Seed Placement Jobs
        print("\n[+] Seeding Placement Jobs into Turso...")
        jobs = [
            ("Software Development Engineer", "Google", "Full-time SDE role building scalable backend and distributed services.", "Python, Java, SQL, Data Structures", 7.5, "CSE, IT", 2027, "approved"),
            ("Frontend Engineer", "Microsoft", "Build high-performance web user interfaces with React and TypeScript.", "React, JavaScript, HTML/CSS, Git", 7.0, "CSE, IT, ECE", 2027, "approved"),
            ("Data Analyst", "Amazon", "Analyze large-scale operational data, design dashboards, and drive business insights.", "Python, SQL, Statistics, Excel, Power BI", 6.5, "CSE, IT, ECE, ME", 2027, "approved"),
            ("Cloud & DevOps Trainee", "CloudSys Solutions", "Manage CI/CD pipelines, containerized deployments, and cloud infrastructure.", "Linux, Docker, AWS, Git", 6.0, "CSE, IT", 2027, "pending")
        ]

        for j in jobs:
            client.execute(
                """
                INSERT OR IGNORE INTO jobs 
                (title, company_name, description, required_skills, minimum_cgpa, eligible_branches, graduation_year, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                list(j)
            )
        print("  - Seeded 4 placement jobs.")

        # 6. Verify row counts
        res_users = client.execute("SELECT COUNT(*) FROM users;")
        res_students = client.execute("SELECT COUNT(*) FROM students;")
        res_jobs = client.execute("SELECT COUNT(*) FROM jobs;")

        print("\n==================================================")
        print("Turso Cloud Database Successfully Synchronized!")
        print("==================================================")
        print(f"  - Total Users in Turso:    {res_users.rows[0][0]}")
        print(f"  - Total Students in Turso: {res_students.rows[0][0]}")
        print(f"  - Total Jobs in Turso:     {res_jobs.rows[0][0]}")
        print("==================================================\n")

    finally:
        client.close()


if __name__ == "__main__":
    push_schema_and_data_to_turso()
