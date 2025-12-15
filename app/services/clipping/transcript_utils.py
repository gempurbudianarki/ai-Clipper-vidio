import os
import json

TRANSCRIPT_DIR = "storage/transcripts"

def load_transcript_json(filename: str) -> dict:
    base = filename.rsplit(".", 1)[0]
    path = os.path.join(TRANSCRIPT_DIR, base + ".json")
    if not os.path.exists(path):
        raise FileNotFoundError("Transcript belum ada. Jalankan transkrip dulu.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def transcript_to_timestamped_text(t: dict, max_segments: int = 500) -> str:
    segs = t.get("segments", [])[:max_segments]
    lines = []
    for s in segs:
        start = s.get("start", 0)
        end = s.get("end", 0)
        text = (s.get("text") or "").strip()
        if text:
            lines.append(f"[{start:.2f} - {end:.2f}] {text}")
    return "\n".join(lines)
