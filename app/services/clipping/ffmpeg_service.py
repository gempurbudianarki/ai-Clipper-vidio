import os
import subprocess
from datetime import datetime

UPLOAD_DIR = "storage/uploads"
CLIPS_DIR = "storage/clips"

os.makedirs(CLIPS_DIR, exist_ok=True)

def ensure_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except Exception:
        raise RuntimeError(
            "ffmpeg tidak ditemukan. Install ffmpeg dulu dan pastikan ada di PATH."
        )

def render_clip(input_filename: str, start: float, end: float) -> str:
    ensure_ffmpeg()

    input_path = os.path.join(UPLOAD_DIR, input_filename)
    if not os.path.exists(input_path):
        raise FileNotFoundError("Video input tidak ditemukan")

    if end <= start:
        raise ValueError("end harus lebih besar dari start")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{input_filename.rsplit('.',1)[0]}_{ts}_{start:.2f}-{end:.2f}.mp4".replace(":", "_")
    out_path = os.path.join(CLIPS_DIR, out_name)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", str(start),
        "-to", str(end),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        out_path
    ]

    subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out_name
