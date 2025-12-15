from faster_whisper import WhisperModel

class WhisperTranscriber:
    def __init__(self, model_size="tiny"):
        # tiny jauh lebih cepat di CPU
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

    def transcribe(self, audio_path: str):
        # vad_filter bantu buang silence, makin cepat
        segments, info = self.model.transcribe(
            audio_path,
            vad_filter=True,
            beam_size=1,
            best_of=1
        )

        result_segments = []
        for s in segments:
            # s.text, s.start, s.end
            result_segments.append({
                "start": float(s.start),
                "end": float(s.end),
                "text": s.text.strip()
            })

        return {
            "language": info.language,
            "duration": info.duration,
            "segments": result_segments
        }
