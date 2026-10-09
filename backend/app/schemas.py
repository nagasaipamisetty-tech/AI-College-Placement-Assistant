from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginInput(BaseModel):
    email: str
    password: str


class StudentRegistration(BaseModel):
    roll_number: str
    email: str
    password: str


class JobCreate(BaseModel):
    title: str
    company_name: str
    description: str = ""
    required_skills: str = ""
    minimum_cgpa: float = 0.0
    eligible_branches: str = ""
    graduation_year: int | None = None


class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationStatusUpdate(BaseModel):
    status: str


class AdminApplicationCreate(BaseModel):
    student_id: int
    job_id: int
    status: str = "applied"


class StudentCreate(BaseModel):
    roll_number: str
    name: str
    email: str
    phone: str | None = ""
    branch: str = ""
    graduation_year: int | None = None
    cgpa: float | None = None
    skills: str = ""
    linkedin_url: str | None = ""
    github_url: str | None = ""
    hackerrank_url: str | None = ""
    leetcode_url: str | None = ""
    portfolio_url: str | None = ""
    bio: str | None = ""


class StudentUpdate(BaseModel):
    roll_number: str | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    cgpa: float | None = None
    skills: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    hackerrank_url: str | None = None
    leetcode_url: str | None = None
    portfolio_url: str | None = None
    bio: str | None = None


class StudentProfileUpdate(BaseModel):
    phone: str | None = None
    skills: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    hackerrank_url: str | None = None
    leetcode_url: str | None = None
    portfolio_url: str | None = None
    bio: str | None = None


class TrainingCreate(BaseModel):
    title: str
    description: str = ""
    trainer: str = ""
    scheduled_at: datetime | None = None
    capacity: int = 50
