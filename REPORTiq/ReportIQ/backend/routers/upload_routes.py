from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import pandas as pd
import uuid

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]

UPLOAD_DIR = ROOT / "static" / "uploads"
REPORTS_DIR = ROOT / "static" / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

from backend.core.data_cleaner import clean_dataset, get_data_quality_score
from backend.core.report_generator import generate_report_assets


@router.post("/", tags=["Upload"])
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file selected")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".csv", ".xlsx"):
        raise HTTPException(400, "Only CSV and Excel allowed")

    file_id = uuid.uuid4().hex[:10]
    saved_path = UPLOAD_DIR / f"{file_id}{ext}"

    with open(saved_path, "wb") as f:
        f.write(await file.read())

    df = pd.read_csv(saved_path) if ext == ".csv" else pd.read_excel(saved_path)

    cleaned = clean_dataset(df)
    cleaned_df = cleaned["cleaned_df"]

    report_dir = REPORTS_DIR / file_id
    report_dir.mkdir(parents=True, exist_ok=True)

    # Save preview HTML
    (report_dir / "raw_data_preview.html").write_text(
        df.head(200).to_html(index=False), encoding="utf-8"
    )
    (report_dir / "cleaned_data_preview.html").write_text(
        cleaned_df.head(200).to_html(index=False), encoding="utf-8"
    )

    # Save plots
    plots = generate_report_assets(cleaned_df, report_dir)

    return {
        "report_id": file_id,
        "plots": [p.name for p in plots],
        "summary": cleaned["summary"],
        "quality": get_data_quality_score(df)
    }
