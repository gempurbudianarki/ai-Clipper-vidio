from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router

app = FastAPI(
    title="AI Video Auto Clip Editor",
    description="AI system for auto clipping and editing videos",
    version="0.2.0"
)

# ✅ API dulu biar /api gak ketangkep StaticFiles
app.include_router(api_router)

# Serve storage outputs (clips, transcripts, uploads) for preview/download
app.mount("/files", StaticFiles(directory="storage"), name="files")

# Serve frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
