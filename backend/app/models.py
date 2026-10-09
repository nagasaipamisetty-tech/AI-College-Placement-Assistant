from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), default="")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="student")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    roll_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True, default="")
    branch: Mapped[str] = mapped_column(String(100), default="")
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    skills: Mapped[str] = mapped_column(Text, default="")
    linkedin_url: Mapped[str | None] = mapped_column(String(300), nullable=True, default="")
    github_url: Mapped[str | None] = mapped_column(String(300), nullable=True, default="")
    hackerrank_url: Mapped[str | None] = mapped_column(String(300), nullable=True, default="")
    leetcode_url: Mapped[str | None] = mapped_column(String(300), nullable=True, default="")
    portfolio_url: Mapped[str | None] = mapped_column(String(300), nullable=True, default="")
    bio: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    raw_data: Mapped[str] = mapped_column(Text, default="{}")
    approved_for_registration: Mapped[bool] = mapped_column(
        Boolean, default=True
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    company_name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    required_skills: Mapped[str] = mapped_column(Text, default="")
    minimum_cgpa: Mapped[float] = mapped_column(Float, default=0.0)
    eligible_branches: Mapped[str] = mapped_column(Text, default="")
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("student_id", "job_id", name="uq_student_job"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    status: Mapped[str] = mapped_column(String(30), default="applied")
    applied_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    trainer: Mapped[str] = mapped_column(String(150), default="")
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    capacity: Mapped[int] = mapped_column(Integer, default=50)
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "training_id", name="uq_student_training"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    training_id: Mapped[int] = mapped_column(
        ForeignKey("training_sessions.id")
    )
    status: Mapped[str] = mapped_column(String(30), default="enrolled")
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )


class InterviewPrepPlan(Base):
    __tablename__ = "interview_prep_plans"
    __table_args__ = (
        UniqueConstraint("student_id", "job_id", name="uq_student_job_plan"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    skill_gaps: Mapped[str] = mapped_column(Text, default="")
    skill_match_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    plan_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )


class AutoApplyReceipt(Base):
    __tablename__ = "auto_apply_receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    confirmation_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    job_id: Mapped[str] = mapped_column(String(100), index=True)
    job_title: Mapped[str] = mapped_column(String(200))
    company_name: Mapped[str] = mapped_column(String(200))
    portal_url: Mapped[str] = mapped_column(Text, default="")
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="SUBMITTED")
    tailored_cover_letter: Mapped[str] = mapped_column(Text, default="")
    custom_qa_json: Mapped[str] = mapped_column(Text, default="{}")
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class TrainingMaterial(Base):
    __tablename__ = "training_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("training_sessions.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    file_name: Mapped[str] = mapped_column(String(300))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50), default="")  # pdf, image, note
    file_size: Mapped[int] = mapped_column(Integer, default=0)  # bytes
    uploaded_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    uploaded_by_name: Mapped[str] = mapped_column(String(150), default="")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)