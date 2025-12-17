import json
import re
from openai import OpenAI
from app.core.config import settings


def extract_json(text: str):
    """
    Versi Robust/Kebal Peluru.
    Mencoba mengekstrak JSON dari teks yang 'kotor' (banyak teks intro/outro dari LLM).
    """
    if not text:
        raise ValueError("Empty response from LLM")

    # 1. Bersihkan Markdown code blocks umum
    cleaned_text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()

    # 2. Coba cari pattern JSON array [...] atau object {...}
    # Menggunakan pattern yang menangkap bracket terluar
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned_text)
    
    candidate = cleaned_text
    if match:
        candidate = match.group(1)
    
    # 3. Usaha parsing pertama: Langsung load
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 4. Usaha parsing kedua: Fix Trailing Commas (Masalah klasik LLM)
    # Hapus koma sebelum penutup ] atau }
    candidate_fixed = re.sub(r",\s*([\]}])", r"\1", candidate)
    try:
        return json.loads(candidate_fixed)
    except json.JSONDecodeError:
        pass

    # 5. Jika masih gagal, raise error dengan snippet teks biar gampang debug
    snippet = text[:200] + "..." if len(text) > 200 else text
    raise ValueError(f"Failed to parse JSON from LLM output. Raw snippet: {snippet}")


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
        """
        Wrapper untuk call API. 
        Temperature rendah untuk logika, Temperature sedang untuk kreatif.
        """
        try:
            res = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=temperature,
            )
            content = res.choices[0].message.content
            if not content:
                raise ValueError("LLM returned empty content")
            return content.strip()
        except Exception as e:
            # Log error di sini sangat penting untuk production
            print(f"[LLM Error] Model: {model} | Error: {str(e)}")
            raise e

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

Return EXACT JSON format like this:
[
  {{"start":12.5,"end":48.0,"reason":"why this is a strong clip"}}
]

Transcript:
{transcript}
"""
        # Temperature sangat rendah (0.05) agar output deterministik dan patuh format
        raw = self._ask(self.model_logic, system, user, temperature=0.05)
        return extract_json(raw)

    def enrich_hooks(self, clips, transcript: str):
        system = (
            "You are a strict JSON API. Return ONLY valid JSON array. "
            "NO explanation. NO markdown. "
            "Hooks must be short, punchy, and scroll-stopping."
        )

        user = f"""
For each clip, write a viral hook line (max 12 words) and a score (0.0 - 1.0).
Hook style: direct, bold, emotionally charged, creator tone.

Return EXACT JSON format:
[
  {{"start":12.5,"end":48.0,"hook":"STOP scrolling. This changes everything.","score":0.88}}
]

Clips Input:
{json.dumps(clips, ensure_ascii=False)}

Transcript Context:
{transcript[:3000]}... (truncated for context)
"""
        # Temperature agak naik (0.35) biar Qwen sedikit kreatif tapi tetap logis
        raw = self._ask(self.model_style, system, user, temperature=0.35)
        return extract_json(raw)

    def generate_clips(self, transcript: str, max_clips: int = 6, min_sec: int = 25, max_sec: int = 60):
        # 1. Tahap Logika (DeepSeek)
        base = self.select_clip_boundaries(transcript, max_clips=max_clips, min_sec=min_sec, max_sec=max_sec)
        
        # Validasi output dari tahap 1
        if not base or not isinstance(base, list):
            print("[Warning] DeepSeek tidak menghasilkan list clip yang valid.")
            return []

        # 2. Tahap Kreatif (Qwen)
        styled = self.enrich_hooks(base, transcript)
        
        # Validasi output dari tahap 2
        if not styled or not isinstance(styled, list):
            print("[Warning] Qwen gagal generate hooks, fallback ke data raw.")
            styled = []

        merged = []
        for b in base:
            # Cari hook yang pas berdasarkan start timestamp
            s = next((x for x in styled if x.get("start") == b.get("start")), {})
            
            merged.append({
                "start": float(b.get("start", 0)),
                "end": float(b.get("end", 0)),
                "reason": b.get("reason", "No reason provided"),
                "hook": s.get("hook", "Watch this!"), # Fallback hook
                "score": float(s.get("score", 0.5)),
            })

        # Sort by score desc biar yang paling bagus di atas
        merged.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return merged
    