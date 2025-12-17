import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.services.subtitle.ass_builder import build_ass_from_timeline
from app.services.subtitle.ffmpeg_subtitle import burn_ass_subtitle

router = APIRouter(prefix="/subtitle", tags=["subtitle"])

STORAGE_TRANSCRIPTS = "storage/transcripts"
STORAGE_ASS = "storage/ass"
STORAGE_EDITS = "storage/edits"
STORAGE_CLIPS = "storage/clips"
STORAGE_OUT = "storage/clips_subtitled"

# === DATA MODELS ===
class WordItem(BaseModel):
    word: str
    start: float
    end: float

class TimelineItem(BaseModel):
    start: float
    end: float
    text: str
    words: Optional[List[WordItem]] = None 

class TimelinePayload(BaseModel):
    transcript_name: str
    clip_start_abs: float
    clip_end_abs: float
    items: List[TimelineItem]
    ratio: str = "9:16"
    style: str = "hormozi"
    hook: str = ""
    bgm: Optional[str] = None # <--- Fitur BGM Filename

# === HELPERS (Sama seperti sebelumnya) ===
def _normalize_transcript_name(name: str) -> str:
    base = name
    if base.lower().endswith(".mp4"): base = base[:-4]
    if base.lower().endswith(".json"): base = base[:-5]
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
    if isinstance(data, dict) and "segments" in data: return data["segments"]
    if isinstance(data, list): return data
    return []

def _default_timeline_from_segments(segments: List[Dict], clip_start_abs: float, clip_end_abs: float) -> List[Dict]:
    out = []
    for seg in segments:
        st = float(seg.get("start", 0))
        ed = float(seg.get("end", st + 0.8))
        text = (seg.get("text") or "").strip()
        words = seg.get("words", [])
        
        if not text: continue
        if ed < clip_start_abs or st > clip_end_abs: continue
        
        rel_st = round(max(st, clip_start_abs) - clip_start_abs, 2)
        rel_ed = round(min(ed, clip_end_abs) - clip_start_abs, 2)
        if rel_ed - rel_st < 0.1: continue

        rel_words = []
        for w in words:
            if w["end"] > clip_start_abs and w["start"] < clip_end_abs:
                rel_words.append({
                    "word": w["word"],
                    "start": round(max(w["start"], clip_start_abs) - clip_start_abs, 2),
                    "end": round(min(w["end"], clip_end_abs) - clip_start_abs, 2)
                })

        out.append({"start": rel_st, "end": rel_ed, "text": text, "words": rel_words})
    return out

# === ENDPOINTS ===

@router.post("/timeline/{clip_file}")
def get_or_build_timeline(clip_file: str, transcript_name: str, clip_start_abs: float, clip_end_abs: float):
    os.makedirs(STORAGE_EDITS, exist_ok=True)
    edit_path = _edit_path(clip_file)

    if os.path.exists(edit_path):
        with open(edit_path, "r", encoding="utf-8") as f:
            return {"source": "edit", "items": json.load(f)}

    segs = _load_transcript_segments(transcript_name)
    items = _default_timeline_from_segments(segs, clip_start_abs, clip_end_abs)

    with open(edit_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    return {"source": "generated", "items": items}

@router.post("/render/{clip_file}")
def render_subtitle_from_timeline(payload: TimelinePayload, clip_file: str):
    clip_path = os.path.join(STORAGE_CLIPS, os.path.basename(clip_file))
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail=f"Clip tidak ditemukan")

    # 1. Save Edit
    os.makedirs(STORAGE_EDITS, exist_ok=True)
    edit_path = _edit_path(clip_file)
    with open(edit_path, "w", encoding="utf-8") as f:
        f.write(payload.model_dump_json(indent=2))

    # 2. Generate ASS (Include Hook)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ass_name = f"{os.path.basename(clip_file)}_{ts}.ass"
    ass_path = os.path.join(STORAGE_ASS, ass_name)
    items_dict = [i.model_dump() for i in payload.items]
    
    build_ass_from_timeline(
        items_dict, 
        ass_path, 
        ratio=payload.ratio, 
        style_name=payload.style,
        hook_text=payload.hook
    )

    # 3. Render (Include BGM & HD settings)
    out_name = f"{os.path.splitext(os.path.basename(clip_file))[0]}_{payload.style}_{ts}.mp4"
    out_path = os.path.join(STORAGE_OUT, out_name)

    try:
        burn_ass_subtitle(
            clip_path, 
            ass_path, 
            out_path, 
            ratio=payload.ratio,
            custom_bgm_file=payload.bgm # Pass Custom BGM
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"url": f"/files/clips_subtitled/{out_name}"}