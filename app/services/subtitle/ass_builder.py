import os
from typing import List, Dict

# ==========================================
# VIZARD STYLE TEMPLATES CONFIGURATION
# ==========================================

STYLES = {
    "hormozi": {
        "font": "Arial Black",
        "fontsize": 80,
        "primary": "&H00FFFFFF",   # Putih
        "secondary": "&H0000FFFF", # Kuning (Highlight Karaoke)
        "outline": "&H00000000",   # Hitam Pekat
        "back": "&H80000000",
        "bold": -1,
        "border_style": 1,
        "outline_width": 4,
        "shadow": 0,
        "uppercase": True
    },
    "neon": {
        "font": "Arial", 
        "fontsize": 80,
        "primary": "&H00FFFFFF",
        "secondary": "&H00FF00FF", # Magenta Neon
        "outline": "&H00FF00FF",   # Glow Magenta
        "back": "&H00000000",
        "bold": -1,
        "border_style": 1,
        "outline_width": 2,
        "shadow": 0,
        "uppercase": False
    },
    "box": {
        "font": "Verdana",
        "fontsize": 70,
        "primary": "&H00000000",   # Teks Hitam
        "secondary": "&H000000FF", # Teks Merah saat aktif
        "outline": "&H00FFFFFF",   # Outline Putih tipis
        "back": "&H00FFFFFF",      # Box Putih
        "bold": -1,
        "border_style": 3,         # Opaque Box Style
        "outline_width": 0,
        "shadow": 0,
        "uppercase": True
    },
    "classic": {
        "font": "Arial",
        "fontsize": 65,
        "primary": "&H00FFFFFF",
        "secondary": "&H0000FFFF",
        "outline": "&H00000000",
        "back": "&H60000000",
        "bold": 0,
        "border_style": 1,
        "outline_width": 2,
        "shadow": 1,
        "uppercase": False
    }
}

def get_header(ratio="9:16", style_name="hormozi"):
    """
    Generate ASS Header dinamis.
    Fix: Style 'Hook' sekarang punya Outline Width = 5 biar kotaknya muncul.
    """
    cfg = STYLES.get(style_name, STYLES["hormozi"])
    
    # Atur resolusi & margin berdasarkan rasio video
    if ratio == "16:9":
        resx, resy = 1920, 1080
        margin_v = 100
        hook_margin_v = 80
        f_scale = 1.0
    elif ratio == "1:1":
        resx, resy = 1080, 1080
        margin_v = 150
        hook_margin_v = 100
        f_scale = 0.9
    else: # Default 9:16 (TikTok/Reels)
        resx, resy = 1080, 1920
        margin_v = 450 # Posisi subtitle (bawah)
        hook_margin_v = 350 # Posisi hook (atas, safe area)
        f_scale = 1.0

    fontsize = int(cfg["fontsize"] * f_scale)
    hook_fontsize = int(65 * f_scale) 
    
    # === STYLE DEFINITION ===
    # Format: ... BorderStyle, Outline, Shadow ...
    
    # STYLE SUBTITLE (Sesuai Pilihan User)
    style_def = f"Style: Default,{cfg['font']},{fontsize},{cfg['primary']},{cfg['secondary']},{cfg['outline']},{cfg['back']},{cfg['bold']},0,0,0,100,100,0,0,{cfg['border_style']},{cfg['outline_width']},{cfg['shadow']},2,50,50,{margin_v},1"
    
    # STYLE HOOK (Vizard Style Fixed)
    # Primary: &H00000000 (Hitam) -> Teks
    # Outline: &H00FFFFFF (Putih) -> Warna Box (Background)
    # BorderStyle: 3 (Opaque Box)
    # Outline Width: 5 (INI KUNCINYA BIAR BOX MUNCUL)
    style_hook = f"Style: Hook,Arial Black,{hook_fontsize},&H00000000,&H00000000,&H00FFFFFF,&H00000000,1,0,0,0,100,100,0,0,3,5,0,8,50,50,{hook_margin_v},1"

    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {resx}
PlayResY: {resy}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_def}
{style_hook}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def sec_to_ass(t):
    if t < 0: t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def split_into_phrases(words_list, max_chars=25):
    phrases = []
    current_phrase = []
    current_len = 0
    
    for w in words_list:
        w_len = len(w["word"])
        if current_phrase and (current_len + w_len > max_chars):
            phrases.append(current_phrase)
            current_phrase = [w]
            current_len = w_len
        else:
            current_phrase.append(w)
            current_len += w_len + 1 
            
    if current_phrase:
        phrases.append(current_phrase)
    return phrases

def build_ass_from_timeline(items: List[Dict], out_path: str, ratio: str = "9:16", style_name: str = "hormozi", hook_text: str = ""):
    """
    Core Logic Generator Subtitle + HOOK.
    """
    cfg = STYLES.get(style_name, STYLES["hormozi"])
    lines = [get_header(ratio, style_name)]
    
    # 1. RENDER HOOK (Jika ada)
    # Hook akan muncul dari detik 0 sampai detik ke-4 saja (Vizard Style)
    if hook_text and items:
        # Format Text: Tambah spasi  biar box-nya agak lebar (padding visual)
        display_hook = f"  {hook_text.upper()}  "
        
        # Layer 1 biar di atas subtitle, durasi fix 4 detik
        lines.append(f"Dialogue: 1,0:00:00.00,{sec_to_ass(4.0)},Hook,,0,0,0,,{display_hook}")

    # 2. RENDER SUBTITLE (Karaoke)
    for seg in items:
        # Safety Fix: Handle None words
        words = seg.get("words")
        if words is None: 
            words = []
        
        # Fallback Logic: Fake words jika edit manual
        if not words:
            seg_text = seg.get("text", "")
            if not seg_text: continue
            
            split_txt = seg_text.split()
            if not split_txt: continue
            
            dur = seg["end"] - seg["start"]
            per_word = dur / len(split_txt)
            t = seg["start"]
            
            for txt in split_txt:
                words.append({"word": txt, "start": t, "end": t + per_word})
                t += per_word

        # Pecah phrase (Vizard style)
        phrases = split_into_phrases(words)
        
        for phrase in phrases:
            if not phrase: continue
            
            p_start = phrase[0]["start"]
            p_end = phrase[-1]["end"]
            
            # Animasi Pop Up
            anim = r"{\fscx85\fscy85\t(0,100,\fscx100\fscy100)}" 
            
            karaoke_part = ""
            prev_end = p_start
            
            for w in phrase:
                dur_cs = int((w["end"] - prev_end) * 100)
                if dur_cs < 1: dur_cs = 1 
                
                txt = w["word"]
                if cfg["uppercase"]: 
                    txt = txt.upper()
                
                # Tag \k mengisi warna Secondary (Highlight)
                karaoke_part += f"{{\\k{dur_cs}}}{txt} "
                prev_end = w["end"]

            line = f"Dialogue: 0,{sec_to_ass(p_start)},{sec_to_ass(p_end)},Default,,0,0,0,,{anim}{karaoke_part.strip()}"
            lines.append(line)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path