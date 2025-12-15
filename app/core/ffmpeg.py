import subprocess

def burn_subtitle(video_path: str, ass_path: str, out_path: str):
    ass_path = ass_path.replace("\\", "/")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"subtitles='{ass_path}'",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "copy",
        out_path
    ]

    subprocess.run(cmd, check=True)
    return out_path
