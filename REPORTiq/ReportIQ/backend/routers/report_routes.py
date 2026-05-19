from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import zipfile
import shutil

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "static" / "reports"

@router.get("/{report_id}", tags=["Report"])
async def get_report(report_id: str):
    folder = REPORTS / report_id

    if not folder.exists():
        raise HTTPException(404, "Report not found")

    plots = [f.name for f in folder.iterdir() if f.suffix == ".png"]

    return {
        "report_id": report_id,
        "plots": plots,
        "raw_html": "raw_data_preview.html",
        "clean_html": "cleaned_data_preview.html"
    }


@router.get("/download/{report_id}", tags=["Report"])
async def download_report(report_id: str):
    """Download complete report as ZIP file"""
    report_folder = REPORTS / report_id
    
    if not report_folder.exists():
        raise HTTPException(404, "Report not found")
    
    # Create ZIP file
    zip_path = REPORTS / f"{report_id}.zip"
    
    try:
        # Create zip file with all report contents
        shutil.make_archive(
            str(REPORTS / report_id),
            'zip',
            report_folder
        )
        
        return FileResponse(
            path=zip_path,
            filename=f"report_{report_id}.zip",
            media_type="application/zip"
        )
    
    except Exception as e:
        raise HTTPException(500, f"Error creating download: {str(e)}")


@router.delete("/delete/{report_id}", tags=["Report"])
async def delete_report(report_id: str):
    """Delete a report and all its files permanently"""
    report_folder = REPORTS / report_id
    zip_file = REPORTS / f"{report_id}.zip"
    
    # Also check for uploaded source files
    upload_dir = ROOT / "static" / "uploads"
    
    if not report_folder.exists():
        raise HTTPException(404, "Report not found")
    
    try:
        # Delete report folder and all contents
        shutil.rmtree(report_folder)
        
        # Delete zip file if exists
        if zip_file.exists():
            zip_file.unlink()
        
        # Delete uploaded source files (CSV/XLSX)
        for ext in ['.csv', '.xlsx']:
            upload_file = upload_dir / f"{report_id}{ext}"
            if upload_file.exists():
                upload_file.unlink()
        
        return {
            "success": True,
            "message": "Report deleted successfully",
            "report_id": report_id
        }
    
    except Exception as e:
        raise HTTPException(500, f"Error deleting report: {str(e)}")
