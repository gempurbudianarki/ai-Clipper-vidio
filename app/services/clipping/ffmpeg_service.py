import os
import subprocess
import logging
from datetime import datetime

# Setup logger biar enak debugging-nya
logger = logging.getLogger(__name__)

# Gunakan absolute path agar aman dipanggil dari mana saja
BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "storage", "uploads")
CLIPS_DIR = os.path.join(BASE_DIR, "storage", "clips")

# Pastikan folder output siap
os.makedirs(CLIPS_DIR, exist_ok=True)

def ensure_ffmpeg():
    """
    Cek apakah FFmpeg terinstall dan bisa dipanggil.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
    except FileNotFoundError:
        raise RuntimeError(
            "CRITICAL: FFmpeg command not found. "
            "Pastikan FFmpeg sudah diinstall dan masuk ke PATH system."
        )
    except Exception as e:
        raise RuntimeError(f"Error checking FFmpeg: {str(e)}")

def render_clip(input_filename: str, start: float, end: float, timeout: int = 120) -> str:
    """
    Render potongan video menggunakan FFmpeg.
    
    Args:
        input_filename: Nama file di folder uploads (contoh: video123.mp4)
        start: Waktu mulai (detik)
        end: Waktu akhir (detik)
        timeout: Batas waktu render per clip dalam detik (default 120s)
        
    Returns:
        Nama file output yang berhasil digenerate.
    """
    ensure_ffmpeg()

    # Validasi input path
    input_path = os.path.join(UPLOAD_DIR, input_filename)
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Video input tidak ditemukan di: {input_path}")

    # Validasi durasi
    duration = end - start
    if duration <= 0:
        raise ValueError(f"Durasi invalid: start={start}, end={end}")

    # Generate nama file output yang unik
    # Format: originalname_TIMESTAMP_START-END.mp4
    clean_name = os.path.splitext(input_filename)[0].replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{clean_name}_{ts}_{start:.2f}-{end:.2f}.mp4".replace(":", "-") # Safety replace : for Windows
    out_path = os.path.join(CLIPS_DIR, out_name)

    # Command FFmpeg Optimized
    # -ss sebelum -i (fast seek)
    # -to untuk durasi spesifik
    # -c:v libx264 -preset veryfast (balance speed/quality)
    cmd = [
        "ffmpeg", 
        "-y",               # Overwrite output tanpa tanya
        "-ss", str(start),  # Fast seek (sebelum input)
        "-i", input_path,
        "-to", str(duration), # Durasi relative terhadap -ss
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",       # Kualitas standar visual bagus
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart", # Biar video bisa di-play di browser sambil loading
        out_path
    ]

    logger.info(f"Rendering clip: {out_name} (Duration: {duration:.2f}s)")
    
    try:
        # Jalankan dengan timeout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=timeout 
        )
        logger.info(f"Success rendering: {out_path}")
        return out_name

    except subprocess.TimeoutExpired:
        # Hapus file sampah jika timeout
        if os.path.exists(out_path):
            os.remove(out_path)
        err_msg = f"FFmpeg timeout after {timeout} seconds rendering {out_name}"
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    except subprocess.CalledProcessError as e:
        # Tangkap error detail dari FFmpeg stderr
        err_msg = (
            f"FFmpeg Error (Exit Code {e.returncode}):\n"
            f"{e.stderr}" # Ini bagian pentingnya, pesan error asli FFmpeg
        )
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    except Exception as e:
        logger.error(f"Unexpected error rendering clip: {str(e)}")
        raise e