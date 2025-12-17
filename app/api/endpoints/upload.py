import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.downloader.yt_service import download_video_from_url

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "storage/uploads"
BGM_DIR = "storage/bgm" # Folder khusus BGM user

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BGM_DIR, exist_ok=True)

class UrlPayload(BaseModel):
    url: str

@router.post("/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file lokal (MP4/MOV)."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload gagal: {str(e)}")

@router.post("/url")
async def fetch_video_from_url(payload: UrlPayload):
    """Download video dari YouTube/TikTok."""
    if not payload.url:
        raise HTTPException(status_code=400, detail="URL kosong")
    
    try:
        filename = download_video_from_url(payload.url)
        return {"filename": filename, "source": "web"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bgm")
async def upload_custom_bgm(file: UploadFile = File(...)):
    """Upload lagu background custom."""
    # Bersihkan nama file
    clean_name = "".join(x for x in file.filename if x.isalnum() or x in "._-")
    file_path = os.path.join(BGM_DIR, clean_name)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": clean_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload BGM gagal: {str(e)}")