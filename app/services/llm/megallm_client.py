import json
import re
from openai import OpenAI
from app.core.config import settings


def extract_json(text: str):
    """Robust JSON extraction."""
    if not text:
        raise ValueError("Empty response from LLM")
    cleaned_text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned_text)
    candidate = match.group(1) if match else cleaned_text
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    candidate_fixed = re.sub(r",\s*([\]}])", r"\1", candidate)
    try:
        return json.loads(candidate_fixed)
    except json.JSONDecodeError:
        snippet = text[:200] + "..." if len(text) > 200 else text
        raise ValueError(f"Failed to parse JSON. Raw: {snippet}")


class MegaLLMClient:
    def __init__(self):
        if not settings.MEGALLM_API_KEY:
            raise RuntimeError("MEGALLM_API_KEY belum diset")

        self.client = OpenAI(api_key=settings.MEGALLM_API_KEY, base_url=settings.MEGALLM_BASE_URL)
        self.model_logic = settings.MODEL_DEEPSEEK
        self.model_style = settings.MODEL_QWEN

    def _ask(self, model: str, system: str, user: str, temperature=0.1):
        try:
            res = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=temperature,
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM Error] {str(e)}")
            raise e

    def select_clip_boundaries(self, transcript: str, max_clips: int, min_sec: int, max_sec: int):
        # SYSTEM PROMPT YANG LEBIH CERDAS & GALAK
        system = (
            "You are a professional Video Editor for viral Shorts (TikTok/Reels). "
            "Your job is to find 'High Retention' segments. "
            "Return ONLY valid JSON array."
        )

        user = f"""
Analyze the transcript and pick {max_clips} VIRAL clips.

CRITICAL RULES:
1. Duration: {min_sec}s to {max_sec}s.
2. CONTEXT IS KING: The clip MUST have a clear beginning (setup) and a strong ending (punchline/lesson). Do NOT cut mid-sentence.
3. CONTENT: Look for controversial opinions, strong advice, secrets, or emotional stories.
4. FORMAT: Return strict JSON.

Transcript:
{transcript}

Return JSON:
[
  {{"start":10.5,"end":45.2,"reason":"Strong hook about money, clear conclusion"}}
]
"""
        # Temperature agak naik biar variatif, tapi tetap logis
        raw = self._ask(self.model_logic, system, user, temperature=0.2)
        return extract_json(raw)

    def enrich_hooks(self, clips, transcript: str):
        system = (
            "You are a Copywriter for viral videos. "
            "Write short, clickbait-style hooks in the language of the transcript (Indonesian)."
        )

        user = f"""
For each clip, write a HOOK (Title) that makes people stop scrolling.
Max 5 words. Use ALL CAPS for impact.
Example: "RAHASIA KAYA MENDADAK", "JANGAN LAKUKAN INI!", "SKILL PALING MAHAL".

Return JSON:
[
  {{"start":10.5,"end":45.2,"hook":"RAHASIA 1 MILIAR","score":0.9}}
]

Clips:
{json.dumps(clips)}

Transcript Context:
{transcript[:2000]}
"""
        raw = self._ask(self.model_style, system, user, temperature=0.4)
        return extract_json(raw)

    def generate_clips(self, transcript: str, max_clips: int = 6, min_sec: int = 25, max_sec: int = 60):
        base = self.select_clip_boundaries(transcript, max_clips, min_sec, max_sec)
        if not base: return []

        styled = self.enrich_hooks(base, transcript)
        if not styled: styled = []

        merged = []
        for b in base:
            s = next((x for x in styled if x.get("start") == b.get("start")), {})
            merged.append({
                "start": float(b.get("start", 0)),
                "end": float(b.get("end", 0)),
                "reason": b.get("reason", ""),
                "hook": s.get("hook", "NONTON SAMPAI HABIS"),
                "score": float(s.get("score", 0.7)),
            })

        merged.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return merged