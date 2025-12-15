import os
import json
from fastapi import APIRouter, HTTPException
from app.services.transcriber.whisper_service import WhisperTranscriber

router = APIRouter(prefix="/transcribe", tags=["Transcription"])

UPLOAD_DIR = "storage/uploads"
TRANSCRIPT_DIR = "storage/transcripts"

if not os.path.exists(TRANSCRIPT_DIR):
    os.makedirs(TRANSCRIPT_DIR)

transcriber = WhisperTranscriber(model_size="tiny")

@router.post("/video/{filename}")
def transcribe_video(filename: str):
    video_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    result = transcriber.transcribe(video_path)

    output_file = filename.rsplit(".", 1)[0] + ".json"
    output_path = os.path.join(TRANSCRIPT_DIR, output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    preview_text = "\n".join(
        seg["text"] for seg in result["segments"][:10]
    )

    return {
        "status": "success",
        "segments": len(result["segments"]),
        "preview": preview_text
    }
