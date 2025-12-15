import os
from typing import List, Dict

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Inter,64,&H00FFFFFF,&H00000000,&H64000000,1,0,1,5,1,2,80,80,160,1
Style: Emph,Inter,74,&H0000FFFF,&H00000000,&H64000000,1,0,1,6,1,2,80,80,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def sec_to_ass(t: float) -> str:
    if t < 0:
        t = 0.0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def is_emph(text: str) -> bool:
    hot = {"STOP","JANGAN","HARUS","SEKARANG","INI","KAMU","KENAPA","BISA","GAGAL","SUKSES","BANGKIT","UBAH"}
    up = (text or "").upper()
    for w in hot:
        if w in up:
            return True
    return False

def build_ass_from_timeline(items: List[Dict], out_path: str, pos_x: int = 540, pos_y: int = 1600):
    """
    items: [{start:float, end:float, text:str}]
    start/end harus RELATIVE (mulai dari 0 clip)
    """
    lines = [ASS_HEADER]
    layer = 0

    for it in items:
        st = float(it.get("start", 0))
        ed = float(it.get("end", st + 0.8))
        txt = (it.get("text") or "").strip()
        if not txt:
            continue
        if ed <= st:
            ed = st + 0.6

        style = "Emph" if is_emph(txt) else "Base"

        # Kinetic: pop + sedikit shake (subtle)
        # \t untuk scale 85%->100% di 120ms
        # \blur0.6 biar halus
        fx = rf"{{\an2\pos({pos_x},{pos_y})\blur0.6\fscx85\fscy85\t(0,120,\fscx100\fscy100)}}"

        line = f"Dialogue: {layer},{sec_to_ass(st)},{sec_to_ass(ed)},{style},,0,0,0,,{fx}{txt}"
        lines.append(line)
        layer += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path
