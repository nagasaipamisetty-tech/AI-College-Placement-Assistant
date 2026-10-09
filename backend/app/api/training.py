
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Student, TrainingSession, Enrollment, TrainingMaterial
from app.schemas import TrainingCreate
from app.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/training", tags=["Training"])

# Directory to store uploaded training materials
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "training"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".txt", ".md", ".docx", ".pptx", ".xlsx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ──────────────────────────────────────────────
# Training Sessions
# ──────────────────────────────────────────────

@router.get("/")
def list_training(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "trainer": t.trainer,
            "scheduled_at": t.scheduled_at,
            "capacity": t.capacity
        }
        for t in db.query(TrainingSession).order_by(
            TrainingSession.id.desc()
        ).all()
    ]


@router.post("/", status_code=201)
def create_training(
    data: TrainingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("training", "admin", "trainer"))
):
    session = TrainingSession(
        **data.model_dump(),
        created_by=user.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "message": "Training session created"}


@router.post("/{training_id}/enroll")
def enroll(
    training_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(
        Student.email == user.email
    ).first()
    training = db.query(TrainingSession).filter(
        TrainingSession.id == training_id
    ).first()

    if not student or not training:
        raise HTTPException(status_code=404, detail="Student or training not found")

    count = db.query(Enrollment).filter(
        Enrollment.training_id == training_id,
        Enrollment.status == "enrolled"
    ).count()

    if count >= training.capacity:
        raise HTTPException(status_code=400, detail="Training session is full")

    existing = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.training_id == training_id
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Already enrolled")

    db.add(Enrollment(
        student_id=student.id,
        training_id=training_id
    ))
    db.commit()
    return {"message": "Enrolled successfully"}


# ──────────────────────────────────────────────
# Training Materials — Upload, List, Delete, Download
# ──────────────────────────────────────────────

@router.post("/materials/upload", status_code=201)
async def upload_material(
    title: str = Form(...),
    description: str = Form(""),
    session_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("training", "trainer", "admin"))
):
    """Upload a PDF, image, or note file. Accessible by trainers and admins."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read and size-check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 50 MB limit.")

    # Determine file type category
    if ext == ".pdf":
        file_type = "pdf"
    elif ext in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        file_type = "image"
    elif ext in {".txt", ".md"}:
        file_type = "note"
    else:
        file_type = "document"

    # Save file with unique name
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / unique_name
    with open(dest_path, "wb") as f:
        f.write(content)

    material = TrainingMaterial(
        session_id=session_id,
        title=title,
        description=description,
        file_name=file.filename,
        file_path=str(dest_path),
        file_type=file_type,
        file_size=len(content),
        uploaded_by=user.id,
        uploaded_by_name=user.name or user.email
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "id": material.id,
        "title": material.title,
        "file_name": material.file_name,
        "file_type": material.file_type,
        "file_size": material.file_size,
        "uploaded_by_name": material.uploaded_by_name,
        "uploaded_at": material.uploaded_at,
        "message": "Material uploaded successfully"
    }


@router.get("/materials")
def list_materials(
    session_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all training materials, optionally filtered by session."""
    query = db.query(TrainingMaterial).order_by(TrainingMaterial.uploaded_at.desc())
    if session_id is not None:
        query = query.filter(TrainingMaterial.session_id == session_id)
    materials = query.all()
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "title": m.title,
            "description": m.description,
            "file_name": m.file_name,
            "file_type": m.file_type,
            "file_size": m.file_size,
            "uploaded_by_name": m.uploaded_by_name,
            "uploaded_at": m.uploaded_at,
            "download_url": f"/api/training/materials/{m.id}/download"
        }
        for m in materials
    ]


@router.get("/materials/{material_id}/download")
def download_material(
    material_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Download or view a training material file."""
    material = db.query(TrainingMaterial).filter(
        TrainingMaterial.id == material_id
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    if not Path(material.file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    media_type_map = {
        "pdf": "application/pdf",
        "image": "image/*",
        "note": "text/plain",
        "document": "application/octet-stream"
    }
    media_type = media_type_map.get(material.file_type, "application/octet-stream")

    return FileResponse(
        path=material.file_path,
        filename=material.file_name,
        media_type=media_type
    )


@router.delete("/materials/{material_id}", status_code=200)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("training", "trainer", "admin"))
):
    """Delete a training material. Only trainers and admins."""
    material = db.query(TrainingMaterial).filter(
        TrainingMaterial.id == material_id
    ).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Remove physical file
    try:
        if Path(material.file_path).exists():
            os.remove(material.file_path)
    except Exception:
        pass

    db.delete(material)
    db.commit()
    return {"message": "Material deleted successfully"}