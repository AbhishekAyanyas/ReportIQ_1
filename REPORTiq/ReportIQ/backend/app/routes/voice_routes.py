"""
Voice Upload & Transcription Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.transcribe_service import TranscriptionService
from app.utils.storage import StorageManager
from app.utils.validators import FileValidator

router = APIRouter()
transcription_service = TranscriptionService()
storage_manager = StorageManager()

@router.post("/upload")
async def upload_voice(file: UploadFile = File(...)):
    """
    Upload voice file for transcription
    Supported: wav, mp3, m4a, ogg, flac
    """
    try:
        # Validate file
        if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Supported: wav, mp3, m4a, ogg, flac"
            )
        
        # Save file
        filepath = await storage_manager.save_voice_file(file)
        
        # Validate saved file
        is_valid, message = FileValidator.validate_audio_file(filepath)
        if not is_valid:
            storage_manager.cleanup_file(filepath)
            raise HTTPException(status_code=400, detail=message)
        
        # Transcribe
        result = transcription_service.transcribe_audio(filepath)
        
        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "filepath": filepath,
            "transcription": result
        })
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/status")
def voice_status():
    """Check voice module status"""
    return {
        "status": "online",
        "module": "voice_transcription",
        "version": "1.0.0"
    }
