import os
import yt_dlp
import uuid
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def download_video_from_url(url: str) -> str:
    """
    Download video dari URL (YouTube/TikTok/IG) menggunakan yt-dlp.
    Versi: TANGGUH (Auto-Retry & Anti-Putus).
    """
    # Generate nama file unik biar gak bentrok
    unique_id = str(uuid.uuid4())[:8]
    # Output template: web_UNIKID_VIDEOID.ext
    output_template = os.path.join(UPLOAD_DIR, f"web_{unique_id}_%(id)s.%(ext)s")

    # OPSI YT-DLP "ANTI BADAI"
    ydl_opts = {
        # Format: Prioritaskan MP4 terbaik
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
        
        # Lokasi Output
        'outtmpl': output_template,
        
        # =========================================
        # FITUR KETAHANAN (RESILIENCE) - BARU!
        # =========================================
        'retries': 20,                # Coba lagi 20x kalau gagal connect
        'fragment_retries': 20,       # Coba lagi 20x kalau putus di tengah jalan
        'skip_unavailable_fragments': False, # Jangan skip bagian error, paksa download
        'keep_fragments': True,       # Simpan part download biar bisa resume
        'socket_timeout': 60,         # Tunggu respon server max 60 detik (jangan cepet nyerah)
        
        # Kebersihan Log
        'noplaylist': True,
        'quiet': False,               # Tampilkan log biar kita tau progress
        'no_warnings': True,
        
        # Post-Processing: Paksa jadi MP4 standar biar FFmpeg gak pusing
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        
        # User Agent (Biar gak dianggap bot)
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        logger.info(f"Downloading URL (High Resilience Mode): {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Extract Info dulu (biar tau judul/durasi kalau perlu)
            info = ydl.extract_info(url, download=True) # download=True langsung sikat
            
            # 2. Dapatkan nama file yang tersimpan
            filename = ydl.prepare_filename(info)
            
            # 3. Koreksi ekstensi (Karena postprocessor mungkin merubah .webm jadi .mp4)
            # Kita cek file apa yang beneran ada di folder
            base, _ = os.path.splitext(filename)
            final_path = filename
            
            if not os.path.exists(filename):
                # Cek apakah ada versi .mp4 nya
                if os.path.exists(base + ".mp4"):
                    final_path = base + ".mp4"
                elif os.path.exists(base + ".mkv"):
                    final_path = base + ".mkv"
            
            if not os.path.exists(final_path):
                raise RuntimeError(f"File hasil download tidak ditemukan: {final_path}")

            logger.info(f"Download Sukses: {final_path}")
            return os.path.basename(final_path)

    except Exception as e:
        logger.error(f"Critical Download Error: {str(e)}")
        # Lempar error biar UI tau
        raise RuntimeError(f"Gagal download (Network/Server Error): {str(e)}")