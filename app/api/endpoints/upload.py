import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "storage/uploads"
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def is_allowed(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


@router.post("/video")
async def upload_video(file: UploadFile = File(...)):
    if not is_allowed(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload video only."
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")

    return {
        "status": "success",
        "filename": safe_filename,
        "path": file_path
    }
