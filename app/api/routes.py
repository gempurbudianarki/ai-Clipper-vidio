from fastapi import APIRouter

# ==============================
# IMPORT ALL ENDPOINT ROUTERS
# ==============================

from app.api.endpoints.upload import router as upload_router
from app.api.endpoints.transcribe import router as transcribe_router
from app.api.endpoints.megallm_clips import router as megallm_clips_router
from app.api.endpoints.subtitle import router as subtitle_router
from app.api.endpoints.download import router as download_router # <--- NEW: Download endpoint


# ==============================
# MAIN API ROUTER
# ==============================

router = APIRouter(prefix="/api")


# ==============================
# HEALTH CHECK
# ==============================

@router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "ai-video-editor",
        "version": "1.0"
    }


# ==============================
# REGISTER ALL API ENDPOINTS
# ==============================

# Video upload (local file / youtube url)
router.include_router(
    upload_router,
    tags=["Upload"]
)

# Whisper / speech-to-text
router.include_router(
    transcribe_router,
    tags=["Transcribe"]
)

# MegaLLM (DeepSeek + Qwen) auto clip generator
router.include_router(
    megallm_clips_router,
    tags=["AI Clips"]
)

# Subtitle kinetic (ASS + ffmpeg)
router.include_router(
    subtitle_router,
    tags=["Subtitle"]
)

# Download System (Secure file serving with rename)
router.include_router(
    download_router,
    tags=["Download"]
)