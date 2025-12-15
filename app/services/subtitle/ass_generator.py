import os

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 640
PlayResY: 360

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,28,&H00FFFFFF,&H00000000,&H64000000,0,0,1,2,0,2,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def sec_to_ass(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def build_ass_from_segments(segments, out_path: str):
    lines = [ASS_HEADER]
    layer = 0

    for seg in segments[:5]:  # LIMIT BIAR AMAN
        start = float(seg.get("start", 0))
        end = float(seg.get("end", start + 2))
        text = seg.get("text", "").strip()

        if not text:
            continue

        line = (
            f"Dialogue: {layer},"
            f"{sec_to_ass(start)},"
            f"{sec_to_ass(end)},"
            f"Default,,0,0,0,,{text}"
        )
        lines.append(line)
        layer += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path
