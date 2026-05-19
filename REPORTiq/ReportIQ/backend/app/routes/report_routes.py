"""
Report Upload & Analysis Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.utils.storage import StorageManager
from app.utils.validators import FileValidator
from pathlib import Path

router = APIRouter()
storage_manager = StorageManager()

@router.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):
    """
    Upload report file for analysis
    Supported: pdf, docx, txt, xlsx
    """
    try:
        # Validate file format
        if not file.filename.lower().endswith(('.pdf', '.docx', '.txt', '.xlsx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Supported: pdf, docx, txt, xlsx"
            )
        
        # Save file
        filepath = await storage_manager.save_report_file(file)
        
        # Validate saved file
        is_valid, message = FileValidator.validate_report_file(filepath)
        if not is_valid:
            storage_manager.cleanup_file(filepath)
            raise HTTPException(status_code=400, detail=message)
        
        # Get file info
        file_path = Path(filepath)
        file_size = file_path.stat().st_size
        
        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "filepath": filepath,
            "file_size": file_size,
            "message": "Report uploaded successfully. Analysis pipeline ready."
        })
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/analyze")
async def analyze_report(file: UploadFile = File(...)):
    """
    Analyze uploaded report
    Returns: summary, entities, sentiment, key_points
    """
    try:
        filepath = await storage_manager.save_report_file(file)
        
        # Placeholder for analysis pipeline
        analysis_result = {
            "status": "success",
            "filename": file.filename,
            "analysis": {
                "summary": "Report analysis pipeline ready - integrate NLP models",
                "entities": [],
                "key_points": [],
                "sentiment": "neutral"
            }
        }
        
        return JSONResponse(analysis_result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")

@router.get("/status")
def report_status():
    """Check report module status"""
    return {
        "status": "online",
        "module": "report_analysis",
        "version": "1.0.0"
    }
