import os
import subprocess

def _ffmpeg_filter_escape_path(p: str) -> str:
    """
    Escape path untuk filter ffmpeg (Windows friendly).
    - pakai forward slashes
    - escape ':' jadi '\:'
    - escape '\' dan "'" buat safety
    """
    p = os.path.abspath(p).replace("\\", "/")
    p = p.replace(":", r"\:")
    p = p.replace("'", r"\'")
    return p

def burn_ass_subtitle(input_video: str, ass_path: str, output_video: str) -> None:
    os.makedirs(os.path.dirname(output_video), exist_ok=True)

    in_vid = os.path.abspath(input_video)
    out_vid = os.path.abspath(output_video)
    ass_abs = os.path.abspath(ass_path)

    # pakai filter ass (libass). Sama kayak subtitles tapi lebih stabil buat .ass
    ass_escaped = _ffmpeg_filter_escape_path(ass_abs)
    vf = f"ass='{ass_escaped}'"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", in_vid,
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "copy",
        out_vid
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "FFMPEG subtitle error:\n"
            + (proc.stdout or "")
            + "\n"
            + (proc.stderr or "")
        )
