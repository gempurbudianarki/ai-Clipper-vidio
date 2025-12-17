from faster_whisper import WhisperModel
import logging

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    def __init__(self, model_size="small"):
        # Gunakan 'small' atau 'medium' untuk hasil karaoke yang akurat.
        # 'tiny' terlalu bodoh untuk menangkap timing per kata dengan presisi.
        logger.info(f"Loading Whisper model: {model_size} (CPU)...")
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path: str):
        logger.info(f"Transcribing (Word Level): {audio_path}")
        
        # word_timestamps=True adalah KUNCI untuk efek Karaoke Vizard style
        segments, info = self.model.transcribe(
            audio_path,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            beam_size=5,
            word_timestamps=True, 
            initial_prompt="Transkrip subtitle video pendek tiktok, bahasa gaul, emosional, cepat."
        )

        result_segments = []
        for s in segments:
            # Ekstrak data detail per kata
            words_data = []
            if s.words:
                for w in s.words:
                    words_data.append({
                        "word": w.word.strip(),
                        "start": w.start,
                        "end": w.end,
                        "score": w.probability
                    })
            
            # Fallback safety jika words kosong (jarang terjadi di whisper modern)
            if not words_data:
                words_data.append({
                    "word": s.text.strip(),
                    "start": s.start,
                    "end": s.end,
                    "score": 1.0
                })

            result_segments.append({
                "start": float(s.start),
                "end": float(s.end),
                "text": s.text.strip(),
                "words": words_data # Array ini yang akan dipakai engine subtitle
            })

        logger.info(f"Transcription done. Language: {info.language}")
        return {
            "language": info.language,
            "duration": info.duration,
            "segments": result_segments
        }