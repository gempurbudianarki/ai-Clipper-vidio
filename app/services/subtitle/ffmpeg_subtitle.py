import os
import subprocess
import logging

logger = logging.getLogger(__name__)

# Default Asset
ASSETS_DIR = os.path.abspath("assets")
DEFAULT_BGM = os.path.join(ASSETS_DIR, "bgm.mp3")
# Custom User Storage
USER_BGM_DIR = os.path.abspath("storage/bgm")

def _ffmpeg_filter_escape_path(p: str) -> str:
    p = os.path.abspath(p).replace("\\", "/")
    p = p.replace(":", r"\:")
    p = p.replace("'", r"\'")
    return p

def burn_ass_subtitle(
    input_video: str, 
    ass_path: str, 
    output_video: str, 
    ratio: str = "9:16",
    custom_bgm_file: str = None # Parameter baru
) -> None:
    
    os.makedirs(os.path.dirname(output_video), exist_ok=True)
    
    in_vid = os.path.abspath(input_video)
    out_vid = os.path.abspath(output_video)
    ass_abs = os.path.abspath(ass_path)
    ass_escaped = _ffmpeg_filter_escape_path(ass_abs)
    
    # 1. Logic Crop (Ratio)
    crop_filter = "null" 
    if ratio == "9:16":
        crop_filter = "crop=ih*(9/16):ih" 
    elif ratio == "1:1":
        crop_filter = "crop=ih:ih"
    
    # 2. Logic Subtitle
    sub_filter = f"ass='{ass_escaped}'"
    video_chain = f"[0:v]{crop_filter}[vcropped];[vcropped]{sub_filter}[vout]"
    
    # 3. Logic Audio (BGM)
    # Cek prioritas: Custom BGM > Default Asset BGM > No BGM
    bgm_path = None
    
    if custom_bgm_file:
        check_path = os.path.join(USER_BGM_DIR, custom_bgm_file)
        if os.path.exists(check_path):
            bgm_path = check_path
    
    if not bgm_path and os.path.exists(DEFAULT_BGM):
        bgm_path = DEFAULT_BGM

    cmd = ["ffmpeg", "-y"]
    cmd.extend(["-i", in_vid]) # Input 0
    
    if bgm_path:
        logger.info(f"Mixing BGM: {bgm_path}")
        cmd.extend(["-stream_loop", "-1", "-i", bgm_path]) # Input 1 (Loop)
        
        # Audio Mixing: 
        # BGM volume 15%, Audio asli 100%
        # 'dropout_transition' biar smooth kalau audio asli putus-putus
        audio_chain = f"[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        
        full_filter = f"{video_chain};{audio_chain}"
        
        cmd.extend([
            "-filter_complex", full_filter,
            "-map", "[vout]", 
            "-map", "[aout]"
        ])
    else:
        logger.warning("No BGM applied.")
        cmd.extend([
            "-filter_complex", video_chain,
            "-map", "[vout]",
            "-map", "0:a"
        ])
    
    # 4. Encoding Quality (HD / 4K Ready)
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "slow",     # Lebih lambat render, tapi kualitas & kompresi lebih bagus
        "-crf", "18",          # 18 = Visually Lossless (Sangat Tajam). Default 23.
        "-c:a", "aac",
        "-b:a", "192k",        # Audio quality tinggi
        "-shortest",           # Stop render kalau video habis
        out_vid
    ])

    logger.info(f"Executing FFmpeg Render...")
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "FFMPEG Render Error:\n" + (proc.stderr or proc.stdout)
        )