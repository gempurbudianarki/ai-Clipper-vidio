import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(prefix="/download", tags=["Download System"])

# Root storage path
STORAGE_ROOT = os.path.abspath("storage")

@router.get("/")
async def download_file(
    path: str = Query(..., description="Relative path file di storage (contoh: clips/video.mp4)"),
    name: str = Query(None, description="Nama file baru (Hook) tanpa ekstensi")
):
    """
    Download file dari server dengan nama custom (sesuai Hook).
    """
    # 1. Security Check: Cegah Directory Traversal (biar gak bisa ambil file sistem)
    safe_path = os.path.normpath(os.path.join(STORAGE_ROOT, path))
    if not safe_path.startswith(STORAGE_ROOT):
        raise HTTPException(status_code=403, detail="Akses ditolak: File di luar storage.")

    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan.")

    # 2. Rename Logic
    original_ext = os.path.splitext(safe_path)[1]
    
    if name:
        # Bersihkan nama file dari karakter aneh (biar valid di Windows/Mac/HP)
        # Hanya izinkan huruf, angka, spasi, dan tanda baca aman
        safe_name = "".join([c for c in name if c.isalnum() or c in " ._-!,'()"]).strip()
        
        # Potong kalau kepanjangan (max 200 char)
        safe_name = safe_name[:200]
        
        # Pastikan ekstensi ngikut file asli
        if not safe_name.lower().endswith(original_ext.lower()):
            final_filename = f"{safe_name}{original_ext}"
        else:
            final_filename = safe_name
    else:
        # Kalau gak ada nama request, pake nama asli
        final_filename = os.path.basename(safe_path)

    # 3. Return File dengan Header Download
    return FileResponse(
        path=safe_path, 
        filename=final_filename, 
        media_type="application/octet-stream"
    )