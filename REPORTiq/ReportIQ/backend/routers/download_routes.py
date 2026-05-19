from fastapi import APIRouter
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
UPLOADS = ROOT / "static" / "uploads"
REPORTS = ROOT / "static" / "reports"
DOWNLOADS_LOG = ROOT / "static" / "downloads.json"

# Ensure downloads.json exists
DOWNLOADS_LOG.parent.mkdir(exist_ok=True, parents=True)
if not DOWNLOADS_LOG.exists():
    with open(DOWNLOADS_LOG, 'w') as f:
        json.dump([], f)


def log_download(file_name, file_type, file_size=0):
    """Log a file download to the downloads.json file"""
    try:
        # Read existing downloads
        with open(DOWNLOADS_LOG, 'r') as f:
            downloads = json.load(f)
        
        # Add new download entry
        download_entry = {
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "downloaded_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "timestamp": datetime.now().timestamp()
        }
        
        downloads.append(download_entry)
        
        # Write back to file
        with open(DOWNLOADS_LOG, 'w') as f:
            json.dump(downloads, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error logging download: {str(e)}")
        return False


@router.post("/track/{file_id}")
async def track_download(file_id: str):
    """Track a file download"""
    try:
        # Check if it's a CSV file or report
        csv_file = UPLOADS / f"{file_id}.csv"
        
        if csv_file.exists():
            file_size = csv_file.stat().st_size
            log_download(f"{file_id}.csv", "CSV", file_size)
            return {"status": "success", "message": f"Download tracked for {file_id}.csv"}
        
        return {"status": "error", "message": "File not found"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/summary")
async def get_download_summary():
    """Get comprehensive download summary and statistics"""
    try:
        with open(DOWNLOADS_LOG, 'r') as f:
            downloads = json.load(f)
        
        if not downloads:
            return {
                "total_downloads": 0,
                "unique_files": 0,
                "total_size_mb": 0,
                "file_types": {},
                "most_downloaded": [],
                "recent_downloads": [],
                "downloads_by_date": {}
            }
        
        # Calculate statistics
        total_downloads = len(downloads)
        file_counts = defaultdict(int)
        file_sizes = defaultdict(int)
        file_types = defaultdict(int)
        downloads_by_date = defaultdict(int)
        
        for download in downloads:
            file_name = download.get("file_name", "unknown")
            file_type = download.get("file_type", "unknown")
            file_size = download.get("file_size", 0)
            downloaded_at = download.get("downloaded_at", "")
            
            file_counts[file_name] += 1
            file_sizes[file_name] += file_size
            file_types[file_type] += 1
            
            # Extract date for downloads by date
            if downloaded_at:
                date = downloaded_at.split(" ")[0]
                downloads_by_date[date] += 1
        
        # Get most downloaded files (top 10)
        most_downloaded = sorted(
            [
                {
                    "file_name": name,
                    "download_count": count,
                    "total_size_mb": round(file_sizes[name] / (1024 * 1024), 2)
                }
                for name, count in file_counts.items()
            ],
            key=lambda x: x["download_count"],
            reverse=True
        )[:10]
        
        # Get recent downloads (last 20)
        recent_downloads = sorted(
            downloads,
            key=lambda x: x.get("timestamp", 0),
            reverse=True
        )[:20]
        
        # Clean up timestamps from response
        for item in recent_downloads:
            item.pop("timestamp", None)
        
        # Calculate total size
        total_size_mb = round(sum(file_sizes.values()) / (1024 * 1024), 2)
        
        # File types summary
        file_types_summary = {
            file_type: count
            for file_type, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        }
        
        # Downloads by date (sorted)
        downloads_by_date_sorted = dict(sorted(downloads_by_date.items()))
        
        return {
            "total_downloads": total_downloads,
            "unique_files": len(file_counts),
            "total_size_mb": total_size_mb,
            "file_types": file_types_summary,
            "most_downloaded": most_downloaded,
            "recent_downloads": recent_downloads,
            "downloads_by_date": downloads_by_date_sorted
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "total_downloads": 0,
            "unique_files": 0
        }


@router.get("/statistics")
async def get_download_statistics():
    """Get simplified download statistics"""
    try:
        with open(DOWNLOADS_LOG, 'r') as f:
            downloads = json.load(f)
        
        file_counts = defaultdict(int)
        file_types = defaultdict(int)
        
        for download in downloads:
            file_name = download.get("file_name", "unknown")
            file_type = download.get("file_type", "unknown")
            file_counts[file_name] += 1
            file_types[file_type] += 1
        
        return {
            "total_downloads": len(downloads),
            "unique_files": len(file_counts),
            "file_types_distribution": dict(file_types),
            "average_downloads_per_file": round(len(downloads) / len(file_counts), 2) if file_counts else 0
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.delete("/clear")
async def clear_downloads():
    """Clear all download logs (admin only)"""
    try:
        with open(DOWNLOADS_LOG, 'w') as f:
            json.dump([], f)
        return {"status": "success", "message": "All download logs cleared"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
