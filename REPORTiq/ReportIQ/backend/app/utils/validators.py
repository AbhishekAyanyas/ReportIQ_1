"""
Validation utilities
"""
from pathlib import Path

class FileValidator:
    ALLOWED_AUDIO = {'.wav', '.mp3', '.m4a', '.ogg', '.flac'}
    ALLOWED_REPORTS = {'.pdf', '.docx', '.txt', '.xlsx'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def validate_audio_file(filepath: str) -> tuple[bool, str]:
        """Validate audio file"""
        try:
            path = Path(filepath)
            
            # Check extension
            if path.suffix.lower() not in FileValidator.ALLOWED_AUDIO:
                return False, f"Invalid audio format. Allowed: {FileValidator.ALLOWED_AUDIO}"
            
            # Check file size
            if path.stat().st_size > FileValidator.MAX_FILE_SIZE:
                return False, "File too large (max 50MB)"
            
            return True, "Valid"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_report_file(filepath: str) -> tuple[bool, str]:
        """Validate report file"""
        try:
            path = Path(filepath)
            
            # Check extension
            if path.suffix.lower() not in FileValidator.ALLOWED_REPORTS:
                return False, f"Invalid report format. Allowed: {FileValidator.ALLOWED_REPORTS}"
            
            # Check file size
            if path.stat().st_size > FileValidator.MAX_FILE_SIZE:
                return False, "File too large (max 50MB)"
            
            return True, "Valid"
        except Exception as e:
            return False, str(e)
