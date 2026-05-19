"""
Storage utility for handling file uploads
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile

class StorageManager:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_voice_file(self, file: UploadFile) -> str:
        """Save uploaded voice file"""
        # Create voice subdirectory
        voice_dir = self.upload_dir / "voice"
        voice_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        ext = Path(file.filename).suffix
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = voice_dir / filename
        
        # Save file
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        return str(filepath)
    
    async def save_report_file(self, file: UploadFile) -> str:
        """Save uploaded report file"""
        # Create reports subdirectory
        report_dir = self.upload_dir / "reports"
        report_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        ext = Path(file.filename).suffix
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = report_dir / filename
        
        # Save file
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
        
        return str(filepath)
    
    def cleanup_file(self, filepath: str) -> bool:
        """Delete temporary file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        return False
