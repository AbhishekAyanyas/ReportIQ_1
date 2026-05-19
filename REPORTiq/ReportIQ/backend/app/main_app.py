"""
REPORTiq FastAPI Main Application
Complete backend with voice transcription and report analysis
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import os

# Import routes
from app.routes import voice_routes, report_routes

# Initialize FastAPI app
app = FastAPI(
    title="REPORTiq Backend API",
    description="Voice Transcription & Report Analysis Engine",
    version="1.0.0"
)

# CORS middleware - allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice_routes.router, prefix="/api/voice", tags=["Voice"])
app.include_router(report_routes.router, prefix="/api/reports", tags=["Reports"])

# Root endpoint
@app.get("/")
def root():
    return {
        "app": "REPORTiq",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "voice": "/api/voice/upload",
            "reports": "/api/reports/upload-report",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "REPORTiq Backend",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

@app.get("/api/status")
def api_status():
    """Get status of all modules"""
    return {
        "status": "online",
        "modules": {
            "voice": "ready",
            "reports": "ready",
            "database": "ready"
        }
    }

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "voice").mkdir(exist_ok=True)
(UPLOAD_DIR / "reports").mkdir(exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
