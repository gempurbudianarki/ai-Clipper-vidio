from fastapi import APIRouter, HTTPException
from app.services.llm.megallm_client import MegaLLMClient
from app.services.clipping.transcript_utils import load_transcript_json, transcript_to_timestamped_text
from app.services.clipping.ffmpeg_service import render_clip

router = APIRouter(prefix="/clips", tags=["Clips (MegaLLM)"])


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def enforce_duration_and_pad(start: float, end: float, video_len: float, min_sec: float, max_sec: float,
                             pad_before: float = 2.0, pad_after: float = 1.0):
    """
    - Majukan start sedikit (buildup)
    - Panjangkan end sedikit (biar gak kepotong)
    - Paksa minimal durasi
    - Clamp ke durasi video
    """
    start = clamp(start - pad_before, 0.0, video_len)
    end = clamp(end + pad_after, 0.0, video_len)

    dur = end - start
    if dur < min_sec:
        need = min_sec - dur
        end = clamp(end + need, 0.0, video_len)

    # kalau malah jadi terlalu panjang, potong end
    dur = end - start
    if dur > max_sec:
        end = start + max_sec

    # final safety
    if end <= start:
        end = min(video_len, start + min_sec)

    return float(start), float(end)


@router.post("/generate/{filename}")
def generate_clips(
    filename: str,
    max_clips: int = 6,
    min_sec: int = 25,
    max_sec: int = 60
):
    """
    Default di-upgrade:
    - max_clips 6 (biar banyak opsi)
    - min_sec 25, max_sec 60 (shorts lebih enak)
    """
    try:
        tjson = load_transcript_json(filename)
        transcript_text = transcript_to_timestamped_text(tjson)

        # perkiraan durasi video dari transcript end terakhir
        segs = tjson.get("segments", [])
        video_len = float(segs[-1]["end"]) if segs else 99999.0

        llm = MegaLLMClient()
        picks = llm.generate_clips(transcript_text, max_clips=max_clips, min_sec=min_sec, max_sec=max_sec)

        if not picks:
            raise RuntimeError("LLM tidak menghasilkan klip")

        # Post-process: paksa durasi + padding
        cleaned = []
        for p in picks:
            s = float(p["start"])
            e = float(p["end"])
            s, e = enforce_duration_and_pad(s, e, video_len, float(min_sec), float(max_sec))
            cleaned.append({
                "start": s,
                "end": e,
                "hook": p.get("hook", ""),
                "reason": p.get("reason", ""),
                "score": float(p.get("score", 0.5)),
            })

        # Render semua clip
        rendered = []
        for c in cleaned[:max_clips]:
            out_name = render_clip(filename, c["start"], c["end"])
            rendered.append({
                **c,
                "file": out_name,
                "url": f"/files/clips/{out_name}"
            })

        return {"status": "success", "total": len(rendered), "clips": rendered}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
