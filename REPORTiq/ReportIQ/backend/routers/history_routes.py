from fastapi import APIRouter
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "static" / "reports"


@router.get("/history", tags=["History"])
async def history():
    all_reports = []

    for folder in REPORTS.iterdir():
        if folder.is_dir():
            all_reports.append({
                "report_id": folder.name,
                "files": [f.name for f in folder.iterdir()]
            })

    return {"reports": all_reports}


@router.get("/statistics", tags=["History"])
async def get_statistics():
    """Get dashboard statistics for all reports"""
    total_reports = 0
    completed_reports = 0
    processing_reports = 0
    failed_reports = 0
    
    recent_reports = []
    
    for folder in REPORTS.iterdir():
        if folder.is_dir():
            total_reports += 1
            
            # Check if report has all required files (completed)
            has_plots = any(f.suffix == '.png' for f in folder.iterdir())
            has_html = (folder / 'raw_data_preview.html').exists()
            
            if has_plots and has_html:
                completed_reports += 1
                status = "completed"
            else:
                # For now, consider incomplete as processing
                processing_reports += 1
                status = "processing"
            
            # Get folder creation time
            created_time = folder.stat().st_ctime
            
            recent_reports.append({
                "report_id": folder.name,
                "status": status,
                "created_at": datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S'),
                "timestamp": created_time
            })
    
    # Sort by timestamp (newest first) and take top 5
    recent_reports.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activity = recent_reports[:5]
    
    # Remove timestamp from response
    for report in recent_activity:
        report.pop('timestamp', None)
    
    return {
        "total_reports": total_reports,
        "completed_reports": completed_reports,
        "processing_reports": processing_reports,
        "failed_reports": failed_reports,
        "success_rate": round((completed_reports / total_reports * 100) if total_reports > 0 else 0, 1),
        "recent_activity": recent_activity
    }
