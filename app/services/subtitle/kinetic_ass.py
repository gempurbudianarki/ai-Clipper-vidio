import os

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Arial,64,&H00FFFFFF,&H00000000,&H64000000,1,0,1,3,0,2,80,80,200,1
Style: Emph,Arial,76,&H0000FFFF,&H00000000,&H64000000,1,0,1,4,0,2,80,80,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def sec_to_ass(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def build_ass(segments: list, out_path: str) -> str:
    lines = [ASS_HEADER]
    layer = 0

    for seg in segments:
        start = float(seg["start"])
        end = float(seg["end"])
        text = seg["text"].strip()
        if not text:
            continue

        words = text.split()
        duration = max(end - start, 0.6)
        per_word = duration / len(words)

        t = start
        for w in words:
            st = t
            ed = min(t + per_word, end)

            style = "Emph" if w.isupper() or w.endswith("!") else "Base"

            anim = (
                r"{\an2\pos(540,1500)"
                r"\fscx70\fscy70"
                r"\t(0,120,\fscx100\fscy100)}"
            )

            lines.append(
                f"Dialogue: {layer},{sec_to_ass(st)},{sec_to_ass(ed)},{style},,0,0,0,,{anim}{w}"
            )
            layer += 1
            t = ed

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path
