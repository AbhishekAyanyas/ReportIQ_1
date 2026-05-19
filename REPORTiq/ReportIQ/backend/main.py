from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
import uvicorn
import logging

# Ensure the backend package root is importable when running this file directly
SCRIPT_DIR = Path(__file__).resolve().parent
PARENT_DIR = SCRIPT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Routers
from backend.routers import upload_routes, report_routes, history_routes, feedback_routes, voice_query_routes, transcription_routes, download_routes

# ============================================
# 🔧 DEVELOPMENT MODE SETTING
# ============================================
DEVELOPMENT_MODE = True  # ✅ Set to False for production
# ============================================

app = FastAPI(title="ReportIQ", version="1.0.0")

# BASE PATH
ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"
LOGS_DIR = ROOT / "logs"

# CREATE DIRECTORIES IF THEY DON'T EXIST
STATIC_DIR.mkdir(exist_ok=True, parents=True)
(STATIC_DIR / "uploads").mkdir(exist_ok=True, parents=True)
(STATIC_DIR / "reports").mkdir(exist_ok=True, parents=True)
(STATIC_DIR / "charts").mkdir(exist_ok=True, parents=True)
TEMPLATES_DIR.mkdir(exist_ok=True, parents=True)
LOGS_DIR.mkdir(exist_ok=True, parents=True)

logger.info(f"ReportIQ started - Development Mode: {DEVELOPMENT_MODE}")

# ============================================
# 🚫 DISABLE CACHE MIDDLEWARE (Development)
# ============================================
if DEVELOPMENT_MODE:
    @app.middleware("http")
    async def disable_cache_middleware(request: Request, call_next):
        """Disable caching for all responses in development mode"""
        response = await call_next(request)
        
        # Set no-cache headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    
    logger.info("✅ Cache disabled - All files will load fresh!")
# ============================================

# CORS Configuration (optional, for API access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STATIC MOUNTS
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/uploads", StaticFiles(directory=STATIC_DIR / "uploads"), name="uploads")
    app.mount("/reports", StaticFiles(directory=STATIC_DIR / "reports"), name="reports")
    app.mount("/charts", StaticFiles(directory=STATIC_DIR / "charts"), name="charts")
    logger.info("Static file mounts configured successfully")
except Exception as e:
    logger.error(f"Error mounting static files: {str(e)}")

# TEMPLATES
try:
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    logger.info("Templates configured successfully")
except Exception as e:
    logger.error(f"Error configuring templates: {str(e)}")

# ROUTERS
try:
    app.include_router(upload_routes.router, prefix="/api/upload", tags=["Upload"])
    app.include_router(report_routes.router, prefix="/api/report", tags=["Report"])
    app.include_router(history_routes.router, prefix="/api/history", tags=["History"])
    app.include_router(feedback_routes.router, prefix="/api/feedback", tags=["Feedback"])
    app.include_router(voice_query_routes.router, prefix="/api/voice", tags=["Voice Query"])
    app.include_router(transcription_routes.router, prefix="/api/transcribe", tags=["Transcription"])
    app.include_router(download_routes.router, prefix="/api/download", tags=["Download Summary"])
    logger.info("All routers configured successfully")
except Exception as e:
    logger.error(f"Error configuring routers: {str(e)}")

# HEALTH CHECK
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": "ReportIQ",
        "version": "1.0.0",
        "development_mode": DEVELOPMENT_MODE
    }

# FRONTEND ROUTES
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading home page: {str(e)}")
        return "<h1>ReportIQ</h1><p>Welcome! Templates loading error.</p>"

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page"""
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return "<h1>Dashboard</h1><p>Dashboard loading error.</p>"

@app.get("/visualizations", response_class=HTMLResponse)
async def visualizations(request: Request):
    """Visualizations page"""
    try:
        return templates.TemplateResponse("visualizations.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading visualizations: {str(e)}")
        return "<h1>Visualizations</h1><p>Visualizations loading error.</p>"

@app.get("/reporthistory", response_class=HTMLResponse)
async def reporthistory(request: Request):
    """Report history page"""
    try:
        return templates.TemplateResponse("reporthistory.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading report history: {str(e)}")
        return "<h1>Report History</h1><p>Report history loading error.</p>"

@app.get("/report", response_class=HTMLResponse)
async def report_details(request: Request):
    """Report details page"""
    try:
        return templates.TemplateResponse("report.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading report details: {str(e)}")
        return "<h1>Report Details</h1><p>Report details loading error.</p>"

@app.get("/feedback-test", response_class=HTMLResponse)
async def feedback_test(request: Request):
    """Feedback test page"""
    try:
        return templates.TemplateResponse("feedback_test.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading feedback test: {str(e)}")
        return "<h1>Test</h1><p>Test page loading error.</p>"

@app.get("/simple-test", response_class=HTMLResponse)
async def simple_test(request: Request):
    """Simple test page"""
    try:
        return templates.TemplateResponse("simple_test.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading simple test: {str(e)}")
        return "<h1>Test</h1><p>Test page loading error.</p>"

@app.get("/download-summary", response_class=HTMLResponse)
async def download_summary(request: Request):
    """Download summary page"""
    try:
        return templates.TemplateResponse("download_summary.html", {"request": request})
    except Exception as e:
        logger.error(f"Error loading download summary: {str(e)}")
        return "<h1>Download Summary</h1><p>Download summary loading error.</p>"

if __name__ == "__main__":
    logger.info("Starting ReportIQ on 127.0.0.1:8000")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
