import os
import sys
from datetime import datetime, timedelta

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import Base, engine, SessionLocal
from app.models import User, Student, Job, TrainingSession, Application
from app.core.security import hash_password
from app.services.csv_import import import_students


def seed_database():
    print("==================================================")
    print("Initializing Database & Seeding Initial Data...")
    print("==================================================")

    # 1. Create all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 2. Seed Default System Users
        default_users = [
            {
                "name": "Placement Administrator",
                "email": "admin@college.edu",
                "password": "Admin@123",
                "role": "admin",
            },
            {
                "name": "Placement Operator",
                "email": "operator@college.edu",
                "password": "Operator@123",
                "role": "operator",
            },
            {
                "name": "Technical Trainer",
                "email": "trainer@college.edu",
                "password": "Trainer@123",
                "role": "training",
            },
            {
                "name": "Google Campus Recruiter",
                "email": "recruiter@google.com",
                "password": "Company@123",
                "role": "company",
            },
            {
                "name": "Demo Student",
                "email": "student@college.edu",
                "password": "Student@123",
                "role": "student",
            },
        ]

        print("\n[+] Seeding Users...")
        for u_data in default_users:
            existing = db.query(User).filter(User.email == u_data["email"].lower()).first()
            if not existing:
                user = User(
                    name=u_data["name"],
                    email=u_data["email"].lower(),
                    password_hash=hash_password(u_data["password"]),
                    role=u_data["role"],
                    is_active=True,
                )
                db.add(user)
                print(f"  - Created user: {u_data['email']} (role: {u_data['role']})")
            else:
                print(f"  - User already exists: {u_data['email']}")
        db.commit()

        # 3. Seed Demo Student Profile
        demo_student = db.query(Student).filter(Student.email == "student@college.edu").first()
        if not demo_student:
            demo_student = Student(
                roll_number="23471A0500",
                name="Demo Student",
                email="student@college.edu",
                branch="CSE",
                graduation_year=2027,
                cgpa=8.5,
                skills="Python, Java, SQL, React, Docker, Data Structures",
                approved_for_registration=True,
            )
            db.add(demo_student)
            print("  - Created Demo Student profile (Roll: 23471A0500)")
            db.commit()

        # 4. Import Students CSV if present
        csv_candidates = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "students_data.csv"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "students_data.csv"),
            os.path.join(os.getcwd(), "data", "students_data.csv"),
        ]
        csv_path = None
        for candidate in csv_candidates:
            if os.path.exists(candidate):
                csv_path = candidate
                break

        if csv_path:
            print(f"\n[+] Importing students from: {os.path.normpath(csv_path)}")
            with open(csv_path, "r", encoding="utf-8") as f:
                res = import_students(f, db)
                print(f"  - CSV Import finished: Added={res['added']}, Updated={res['updated']}, Skipped={res['skipped']}")
        else:
            print("\n[-] No students_data.csv found to import.")

        # 5. Seed Jobs
        print("\n[+] Seeding Placement Jobs...")
        jobs_data = [
            {
                "title": "Software Development Engineer",
                "company_name": "Google",
                "description": "Full-time SDE role building scalable backend and distributed services.",
                "required_skills": "Python, Java, SQL, Data Structures",
                "minimum_cgpa": 7.5,
                "eligible_branches": "CSE, IT",
                "graduation_year": 2027,
                "status": "approved",
            },
            {
                "title": "Frontend Engineer",
                "company_name": "Microsoft",
                "description": "Build high-performance web user interfaces with React and TypeScript.",
                "required_skills": "React, JavaScript, HTML/CSS, Git",
                "minimum_cgpa": 7.0,
                "eligible_branches": "CSE, IT, ECE",
                "graduation_year": 2027,
                "status": "approved",
            },
            {
                "title": "Data Analyst",
                "company_name": "Amazon",
                "description": "Analyze large-scale operational data, design dashboards, and drive business insights.",
                "required_skills": "Python, SQL, Statistics, Excel, Power BI",
                "minimum_cgpa": 6.5,
                "eligible_branches": "CSE, IT, ECE, ME",
                "graduation_year": 2027,
                "status": "approved",
            },
            {
                "title": "Cloud & DevOps Trainee",
                "company_name": "CloudSys Solutions",
                "description": "Manage CI/CD pipelines, containerized deployments, and cloud infrastructure.",
                "required_skills": "Linux, Docker, AWS, Git",
                "minimum_cgpa": 6.0,
                "eligible_branches": "CSE, IT",
                "graduation_year": 2027,
                "status": "pending",
            },
        ]

        for j_data in jobs_data:
            existing_job = db.query(Job).filter(
                Job.title == j_data["title"],
                Job.company_name == j_data["company_name"]
            ).first()
            if not existing_job:
                job = Job(**j_data)
                db.add(job)
                print(f"  - Created job: {j_data['title']} @ {j_data['company_name']} ({j_data['status']})")
            else:
                print(f"  - Job already exists: {j_data['title']} @ {j_data['company_name']}")
        db.commit()

        # 6. Seed Training Sessions
        print("\n[+] Seeding Training Sessions...")
        now = datetime.now()
        training_data = [
            {
                "title": "DSA & LeetCode Intensive Masterclass",
                "description": "Hands-on problem solving covering Graphs, Dynamic Programming, and System Design.",
                "trainer": "Technical Trainer",
                "scheduled_at": now + timedelta(days=7),
                "capacity": 100,
            },
            {
                "title": "Full Stack Web Development with React & FastAPI",
                "description": "Build end-to-end full stack applications with secure authentication and modern APIs.",
                "trainer": "Technical Trainer",
                "scheduled_at": now + timedelta(days=14),
                "capacity": 60,
            },
            {
                "title": "Aptitude, Soft Skills & Mock Interview Preparation",
                "description": "Quantitative aptitude training and live mock HR/Technical interview sessions.",
                "trainer": "Placement Cell",
                "scheduled_at": now + timedelta(days=21),
                "capacity": 150,
            },
        ]

        for t_data in training_data:
            existing_training = db.query(TrainingSession).filter(
                TrainingSession.title == t_data["title"]
            ).first()
            if not existing_training:
                t = TrainingSession(**t_data)
                db.add(t)
                print(f"  - Created training session: {t_data['title']}")
            else:
                print(f"  - Training session already exists: {t_data['title']}")
        db.commit()

        print("\n==================================================")
        print("Seeding Completed Successfully!")
        print("==================================================")
        print("\nDefault Credentials:")
        print("  - Admin:     admin@college.edu     / Admin@123")
        print("  - Operator:  operator@college.edu  / Operator@123")
        print("  - Trainer:   trainer@college.edu   / Trainer@123")
        print("  - Company:   recruiter@google.com  / Company@123")
        print("  - Student:   student@college.edu   / Student@123")
        print("==================================================\n")

    except Exception as e:
        db.rollback()
        print(f"\n[!] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()