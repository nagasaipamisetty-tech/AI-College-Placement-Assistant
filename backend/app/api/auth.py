
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Student
from app.schemas import LoginInput, StudentRegistration
from app.core.security import (
    verify_password, hash_password, create_access_token
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login")
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email.lower()
    ).first()

    if not user or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return {
        "access_token": create_access_token(user.email),
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


@router.post("/register-student", status_code=201)
def register_student(
    data: StudentRegistration,
    db: Session = Depends(get_db)
):
    email = data.email.lower().strip()
    roll = data.roll_number.strip()

    approved = db.query(Student).filter(
        Student.roll_number == roll,
        Student.email == email,
        Student.approved_for_registration.is_(True)
    ).first()

    if not approved:
        raise HTTPException(
            status_code=403,
            detail="Your roll number and email must match the college-approved student list."
        )

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Account already exists")

    user = User(
        name=approved.name,
        email=email,
        password_hash=hash_password(data.password),
        role="student"
    )
    db.add(user)
    db.commit()

    return {"message": "Registration successful. You can now log in."}