"""
Voice Transcription Service
faster-whisper (local, free) — no API key needed
Supported formats: wav, mp3, m4a, ogg, flac, webm
"""
import os
import time
from pathlib import Path

# faster-whisper lazy import — only load when first used (heavy model)
_model = None
_model_size = None


def _get_model(size: str = "base"):
    """Load model once and reuse (singleton pattern)."""
    global _model, _model_size
    if _model is None or _model_size != size:
        from faster_whisper import WhisperModel
        # device="cpu", compute_type="int8" — runs on any machine without GPU
        _model = WhisperModel(size, device="cpu", compute_type="int8")
        _model_size = size
    return _model


ALLOWED_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}
MAX_FILE_SIZE_MB = 50


class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        """
        model_size options (tradeoff: speed vs accuracy):
          "tiny"   — fastest, least accurate (~32 MB)
          "base"   — good balance (default, ~74 MB)
          "small"  — better accuracy (~244 MB)
          "medium" — high accuracy (~769 MB)
        """
        self.model_size = model_size

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transcribe_audio(self, filepath: str) -> dict:
        """
        Transcribe an audio file to text using faster-whisper.

        Returns:
            {
                "status": "success",
                "text": "...",
                "language": "en",
                "duration_seconds": 12.4,
                "segments": [ {"start": 0.0, "end": 3.2, "text": "..."}, ... ]
            }
        """
        path = Path(filepath)

        # Validate before loading model
        valid, error = self._validate(path)
        if not valid:
            return {"status": "error", "message": error}

        try:
            model = _get_model(self.model_size)

            t0 = time.time()
            segments_iter, info = model.transcribe(
                str(path),
                beam_size=5,
                # language=None → auto-detect (supports Hindi, English, etc.)
            )

            segments = []
            full_text_parts = []
            for seg in segments_iter:
                segments.append({
                    "start": round(seg.start, 2),
                    "end":   round(seg.end, 2),
                    "text":  seg.text.strip(),
                })
                full_text_parts.append(seg.text.strip())

            elapsed = round(time.time() - t0, 2)
            full_text = " ".join(full_text_parts)

            return {
                "status": "success",
                "text": full_text,
                "language": info.language,
                "language_probability": round(info.language_probability, 3),
                "duration_seconds": round(info.duration, 2),
                "processing_time_seconds": elapsed,
                "model_used": self.model_size,
                "segments": segments,
            }

        except ImportError:
            return {
                "status": "error",
                "message": (
                    "faster-whisper not installed. "
                    "Run: pip install faster-whisper"
                ),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def validate_audio_file(self, filepath: str) -> bool:
        """Quick boolean check (used by upload validators)."""
        valid, _ = self._validate(Path(filepath))
        return valid

    def get_supported_formats(self) -> list:
        return sorted(ALLOWED_FORMATS)

    def get_model_info(self) -> dict:
        return {
            "model_size": self.model_size,
            "device": "cpu",
            "compute_type": "int8",
            "loaded": _model is not None,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate(self, path: Path):
        if not path.exists():
            return False, f"File not found: {path}"

        ext = path.suffix.lower()
        if ext not in ALLOWED_FORMATS:
            return False, (
                f"Unsupported format '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_FORMATS))}"
            )

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return False, (
                f"File too large ({size_mb:.1f} MB). "
                f"Max allowed: {MAX_FILE_SIZE_MB} MB"
            )

        return True, None
