import os
import subprocess
from datetime import datetime

CLIPS_DIR = os.path.abspath("storage/clips")
OUT_DIR = os.path.abspath("storage/clips_subtitled")

def burn_ass(input_clip: str, ass_path: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)

    inp = os.path.join(CLIPS_DIR, input_clip)
    ass_abs = os.path.abspath(ass_path)

    out_name = f"{os.path.splitext(input_clip)[0]}_sub_{datetime.now().strftime('%H%M%S')}.mp4"
    outp = os.path.join(OUT_DIR, out_name)

    ass_ff = ass_abs.replace("\\", "/")

    cmd = [
        "ffmpeg", "-y",
        "-i", inp,
        "-vf", f"subtitles='{ass_ff}'",
        "-c:v", "libx264",
        "-crf", "20",
        "-preset", "veryfast",
        "-c:a", "copy",
        outp
    ]

    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)

    return out_name
