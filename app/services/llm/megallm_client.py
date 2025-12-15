import json
import re
from openai import OpenAI
from app.core.config import settings


def extract_json(text: str):
    if not text:
        raise ValueError("Empty response from LLM")

    text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
    match = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in LLM output: {text[:200]}")
    return json.loads(match.group(1))


class MegaLLMClient:
    def __init__(self):
        if not settings.MEGALLM_API_KEY:
            raise RuntimeError("MEGALLM_API_KEY belum diset")

        self.client = OpenAI(api_key=settings.MEGALLM_API_KEY, base_url=settings.MEGALLM_BASE_URL)

        self.model_logic = settings.MODEL_DEEPSEEK
        self.model_style = settings.MODEL_QWEN

        if not self.model_logic or not self.model_style:
            raise RuntimeError("MODEL_DEEPSEEK / MODEL_QWEN belum diset")

    def _ask(self, model: str, system: str, user: str, temperature=0.1):
        res = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=temperature,
        )
        return res.choices[0].message.content.strip()

    def select_clip_boundaries(self, transcript: str, max_clips: int, min_sec: int, max_sec: int):
        system = (
            "You are a strict JSON API. Return ONLY valid JSON array. "
            "NO explanation. NO markdown. NO extra text."
        )

        user = f"""
Pick up to {max_clips} best viral short clips from the transcript.

Hard rules:
- Each clip duration MUST be between {min_sec} and {max_sec} seconds.
- Clips MUST NOT overlap.
- Prefer clear emotional / motivational statements, strong claims, conflict, advice.
- Avoid fillers, greetings, low-signal talk.

Return EXACT JSON:
[
  {{"start":12.5,"end":48.0,"reason":"why this is a strong clip"}}
]

Transcript:
{transcript}
""".strip()

        raw = self._ask(self.model_logic, system, user, temperature=0.05)
        return extract_json(raw)

    def enrich_hooks(self, clips, transcript: str):
        system = (
            "You are a strict JSON API. Return ONLY valid JSON array. "
            "NO explanation. NO markdown. "
            "Hooks must be short, punchy, and scroll-stopping."
        )

        user = f"""
For each clip, write a viral hook line (max 12 words) and a score (0-1).
Hook style: direct, bold, emotionally charged, creator tone.

Return EXACT JSON:
[
  {{"start":12.5,"end":48.0,"hook":"STOP scrolling. This changes everything.","score":0.88}}
]

Clips:
{json.dumps(clips, ensure_ascii=False)}

Transcript:
{transcript}
""".strip()

        raw = self._ask(self.model_style, system, user, temperature=0.35)
        return extract_json(raw)

    def generate_clips(self, transcript: str, max_clips: int = 6, min_sec: int = 25, max_sec: int = 60):
        base = self.select_clip_boundaries(transcript, max_clips=max_clips, min_sec=min_sec, max_sec=max_sec)
        styled = self.enrich_hooks(base, transcript)

        merged = []
        for b in base:
            s = next((x for x in styled if x.get("start") == b.get("start")), {})
            merged.append({
                "start": float(b["start"]),
                "end": float(b["end"]),
                "reason": b.get("reason", ""),
                "hook": s.get("hook", ""),
                "score": float(s.get("score", 0.5)),
            })

        # sort by score desc biar yang paling bagus di atas
        merged.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return merged
