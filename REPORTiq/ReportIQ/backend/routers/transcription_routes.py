"""
Transcription Routes
POST /api/transcribe/upload  — audio file upload karo, text wapas milega
GET  /api/transcribe/status  — service status aur model info
GET  /api/transcribe/formats — supported audio formats
"""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.app.services.transcribe_service import TranscriptionService

router = APIRouter()

# Temp folder for uploaded audio files
ROOT = Path(__file__).resolve().parents[2]
AUDIO_UPLOAD_DIR = ROOT / "static" / "uploads" / "audio"
AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# One shared service instance (model loads once)
_svc = TranscriptionService(model_size="base")


# -----------------------------------------------------------------------
# POST /api/transcribe/upload
# -----------------------------------------------------------------------
@router.post("/upload", tags=["Transcription"])
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Audio file upload karo aur transcribed text wapas lo.

    - Supported: wav, mp3, m4a, ogg, flac, webm
    - Max size: 50 MB
    - Model: faster-whisper base (CPU, no GPU needed)
    - Language: auto-detect (Hindi, English, dono support)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Koi file select nahi ki.")

    ext = Path(file.filename).suffix.lower()
    allowed = _svc.get_supported_formats()
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Format '{ext}' supported nahi. Allowed: {', '.join(allowed)}",
        )

    # Save uploaded file temporarily
    file_id = uuid.uuid4().hex[:10]
    save_path = AUDIO_UPLOAD_DIR / f"{file_id}{ext}"

    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save nahi hui: {e}")

    # Transcribe
    result = _svc.transcribe_audio(str(save_path))

    # Clean up temp file
    try:
        save_path.unlink()
    except Exception:
        pass  # Non-critical

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return JSONResponse(content={
        "success": True,
        "filename": file.filename,
        **result,
    })


# -----------------------------------------------------------------------
# GET /api/transcribe/status
# -----------------------------------------------------------------------
@router.get("/status", tags=["Transcription"])
async def transcription_status():
    """Service status aur model info check karo."""
    model_info = _svc.get_model_info()
    return {
        "service": "faster-whisper",
        "status": "ready",
        "model": model_info,
        "supported_formats": _svc.get_supported_formats(),
        "max_file_size_mb": 50,
        "note": (
            "Pehli baar transcribe karne pe model download hoga (~74 MB for base). "
            "Baad mein instant start hoga."
        ),
    }


# -----------------------------------------------------------------------
# GET /api/transcribe/formats
# -----------------------------------------------------------------------
@router.get("/formats", tags=["Transcription"])
async def supported_formats():
    """Supported audio formats ki list."""
    return {
        "formats": _svc.get_supported_formats(),
        "max_size_mb": 50,
    }


# -----------------------------------------------------------------------
# POST /api/transcribe/change-model
# -----------------------------------------------------------------------
@router.post("/change-model", tags=["Transcription"])
async def change_model(model_size: str):
    """
    Model size change karo (tiny/base/small/medium).
    Tradeoff: bada model = zyada accurate, zyada slow.
    """
    global _svc
    valid_sizes = ["tiny", "base", "small", "medium"]
    if model_size not in valid_sizes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model size. Choose from: {valid_sizes}",
        )
    _svc = TranscriptionService(model_size=model_size)
    return {
        "success": True,
        "message": f"Model '{model_size}' set ho gaya. Pehli request pe load hoga.",
        "model_info": _svc.get_model_info(),
    }
