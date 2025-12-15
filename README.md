

```md
<div align="center">

# 🎬 AI Video Editor Studio

⚡ **AI-Powered Automated Video Editing Platform**  
✂️ Auto Clips • 🧠 AI Reasoning • 🧩 Timeline Subtitle Editor • 🔥 Kinetic Subtitle

---

![status](https://img.shields.io/badge/status-active-success)
![backend](https://img.shields.io/badge/backend-FastAPI-009688)
![frontend](https://img.shields.io/badge/frontend-TailwindCSS-38BDF8)
![ai](https://img.shields.io/badge/AI-Whisper%20%7C%20DeepSeek%20%7C%20Qwen-purple)
![video](https://img.shields.io/badge/video-FFmpeg-red)
![license](https://img.shields.io/badge/license-MIT-blue)

</div>

---

## 🧠 Tentang Project

**AI Video Editor Studio** adalah aplikasi **video editing berbasis AI** yang dibuat untuk **content creator modern**  
(TikTok, Instagram Reels, YouTube Shorts, YouTube).

Bukan sekadar auto-cut, sistem ini:
- Memahami **isi video**
- Mendeteksi **momen paling engaging**
- Menghasilkan **clip siap upload**
- Menyediakan **timeline subtitle editor**
- Mendukung **kinetic subtitle (burn-in)**

🎯 Fokus utama:
> **Cepat • Presisi • Bisa diedit manual • Siap produksi**

---

## ✨ Fitur Utama

### 🎥 Video Processing
- Upload video lokal (MP4, MOV, AVI)
- Audio extraction otomatis
- Video rendering via FFmpeg

### 🧠 AI Intelligence
- **Whisper** → Speech-to-Text (transcript)
- **DeepSeek** → Reasoning & highlight detection
- **Qwen** → Hook & narasi clip

### ✂️ AI Auto Clip Generator
- Pemilihan momen terbaik otomatis
- Durasi fleksibel (15–60 detik)
- Skor kualitas setiap clip

### 🧩 Timeline Subtitle Editor
- Edit subtitle per baris
- Atur start / end time manual
- Reorder subtitle
- Preview sebelum render

### 🔥 Kinetic Subtitle
- Generate subtitle format **ASS**
- Burn subtitle langsung ke video
- Style subtitle cinematic & modern

### 🎨 UI Modern
- Glassmorphism
- TailwindCSS
- Animasi halus
- Modal timeline editor

---

## 🏗️ Arsitektur Project

```

ai-video-editor/
│
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── endpoints/
│   │       ├── upload.py
│   │       ├── transcribe.py
│   │       ├── megallm_clips.py
│   │       └── subtitle.py
│   │
│   ├── core/
│   │   ├── ai_logic.py
│   │   └── video_pipeline.py
│   │
│   └── utils/
│       └── helpers.py
│
├── static/
│   └── index.html
│
├── storage/
│   ├── uploads/
│   ├── transcripts/
│   ├── clips/
│   ├── ass/
│   └── final/
│
├── main.py
├── requirements.txt
└── README.md

````

---

## 🚀 Cara Menjalankan (Local Development)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/USERNAME/ai-video-editor.git
cd ai-video-editor
````

---

### 2️⃣ Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### 3️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚠️ PENTING — Install FFmpeg (WAJIB)

FFmpeg digunakan untuk:

* Cutting video
* Rendering clip
* Burn subtitle ASS
* Encoding video final

Cek apakah sudah ter-install:

```bash
ffmpeg -version
```

### Install FFmpeg

**Windows**

* Download: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
* Tambahkan folder `ffmpeg/bin` ke **PATH**

**Linux (Ubuntu / Debian)**

```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS**

```bash
brew install ffmpeg
```

> ❗ Tanpa FFmpeg, fitur clip & subtitle **TIDAK akan jalan**

---

### 4️⃣ Jalankan Server

```bash
uvicorn main:app --reload
```

Buka di browser:

```
http://127.0.0.1:8000
```

---

## 🖥️ Alur Penggunaan Aplikasi

1️⃣ Upload Video
2️⃣ Transcribe Audio (Whisper)
3️⃣ Generate AI Clips
4️⃣ Pilih Clip Terbaik
5️⃣ Edit Subtitle di Timeline
6️⃣ Render Subtitle (Burn-in)
7️⃣ Download Video Final

---

## 📦 Struktur Output

| Folder         | Fungsi                    |
| -------------- | ------------------------- |
| `uploads/`     | Video asli                |
| `transcripts/` | Hasil transkripsi Whisper |
| `clips/`       | Clip hasil AI             |
| `ass/`         | Subtitle ASS              |
| `final/`       | Video final               |

---

## 🧰 Teknologi yang Digunakan

| Layer        | Teknologi             |
| ------------ | --------------------- |
| Backend      | FastAPI               |
| AI STT       | Whisper               |
| AI Reasoning | DeepSeek              |
| AI Language  | Qwen                  |
| Video        | FFmpeg                |
| Subtitle     | ASS                   |
| Frontend     | HTML, TailwindCSS, JS |
| Server       | Uvicorn               |

---

## ⚠️ Catatan

* Project masih **aktif dikembangkan**
* Beberapa AI logic masih **eksperimental**
* Disarankan:

  * RAM ≥ 8GB
  * Storage cukup (video besar)

---

## 🛣️ Roadmap

* [ ] Realtime progress (WebSocket)
* [ ] Preset TikTok / IG / YouTube
* [ ] Music beat sync
* [ ] Multi-language subtitle
* [ ] Docker support

---

## 🤝 Kontribusi

Pull request sangat terbuka.
Fork → eksplor → improve → PR 🚀

---

## 📄 Lisensi

MIT License

---

<div align="center">

🔥 **Built for creators. Designed for scale.**
🚀 *AI Video Editor Studio*

</div>
```

---
