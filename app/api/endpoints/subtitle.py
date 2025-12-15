import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.services.subtitle.ass_builder import build_ass_from_timeline
from app.services.subtitle.ffmpeg_subtitle import burn_ass_subtitle

router = APIRouter(prefix="/subtitle", tags=["subtitle"])

STORAGE_TRANSCRIPTS = "storage/transcripts"
STORAGE_ASS = "storage/ass"
STORAGE_EDITS = "storage/edits"
STORAGE_CLIPS = "storage/clips"
STORAGE_OUT = "storage/clips_subtitled"

class TimelineItem(BaseModel):
    start: float
    end: float
    text: str

class TimelinePayload(BaseModel):
    transcript_name: str
    clip_start_abs: float  # start di video original (detik)
    clip_end_abs: float
    items: List[TimelineItem]

def _normalize_transcript_name(name: str) -> str:
    # kalau user kirim "xxx.mp4" -> jadi "xxx"
    base = name
    if base.lower().endswith(".mp4"):
        base = base[:-4]
    if base.lower().endswith(".json"):
        base = base[:-5]
    return base

def _transcript_path(transcript_name: str) -> str:
    base = _normalize_transcript_name(transcript_name)
    return os.path.join(STORAGE_TRANSCRIPTS, f"{base}.json")

def _edit_path(clip_file: str) -> str:
    base = os.path.basename(clip_file)
    return os.path.join(STORAGE_EDITS, f"{base}.timeline.json")

def _load_transcript_segments(transcript_name: str) -> List[Dict]:
    path = _transcript_path(transcript_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Transcript tidak ditemukan: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # fleksibel: bisa "segments" atau langsung list
    if isinstance(data, dict) and "segments" in data:
        return data["segments"]
    if isinstance(data, list):
        return data
    return []

def _default_timeline_from_segments(segments: List[Dict], clip_start_abs: float, clip_end_abs: float) -> List[Dict]:
    """
    Ambil segment di range clip [start_abs, end_abs], lalu SHIFT ke timebase clip (start=0).
    """
    out = []
    for seg in segments:
        st = float(seg.get("start", 0))
        ed = float(seg.get("end", st + 0.8))
        text = (seg.get("text") or "").strip()
        if not text:
            continue

        # pilih yang overlap
        if ed < clip_start_abs or st > clip_end_abs:
            continue

        # clamp ke range clip
        st2 = max(st, clip_start_abs)
        ed2 = min(ed, clip_end_abs)

        # shift relatif
        rel_st = st2 - clip_start_abs
        rel_ed = ed2 - clip_start_abs

        # buang yang kependekan
        if rel_ed - rel_st < 0.12:
            continue

        out.append({"start": round(rel_st, 2), "end": round(rel_ed, 2), "text": text})
    return out

@router.post("/timeline/{clip_file}")
def get_or_build_timeline(clip_file: str, transcript_name: str, clip_start_abs: float, clip_end_abs: float):
    """
    Return timeline untuk editor.
    Kalau sudah ada edit -> return edit.
    Kalau belum -> build dari transcript (sync bener).
    """
    os.makedirs(STORAGE_EDITS, exist_ok=True)
    edit_path = _edit_path(clip_file)

    if os.path.exists(edit_path):
        with open(edit_path, "r", encoding="utf-8") as f:
            return {"source": "edit", "items": json.load(f)}

    segs = _load_transcript_segments(transcript_name)
    items = _default_timeline_from_segments(segs, clip_start_abs, clip_end_abs)

    # simpan baseline agar consistent
    with open(edit_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    return {"source": "generated", "items": items}

@router.post("/render/{clip_file}")
def render_subtitle_from_timeline(payload: TimelinePayload, clip_file: str):
    """
    Terima timeline hasil edit -> generate ASS -> burn -> return url video subtitled.
    """
    clip_path = os.path.join(STORAGE_CLIPS, os.path.basename(clip_file))
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail=f"Clip tidak ditemukan: {clip_path}")

    # simpan timeline edit
    os.makedirs(STORAGE_EDITS, exist_ok=True)
    edit_path = _edit_path(clip_file)
    items = [i.model_dump() for i in payload.items]
    with open(edit_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    # generate ASS
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ass_name = f"{os.path.basename(clip_file)}_{ts}.ass"
    ass_path = os.path.join(STORAGE_ASS, ass_name)
    build_ass_from_timeline(items, ass_path)

    # burn ke video
    out_name = f"{os.path.splitext(os.path.basename(clip_file))[0]}_sub_{ts}.mp4"
    out_path = os.path.join(STORAGE_OUT, out_name)

    try:
        burn_ass_subtitle(clip_path, ass_path, out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"url": f"/files/clips_subtitled/{out_name}", "ass": f"/files/ass/{ass_name}"}
