from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any

router = APIRouter()

ROOT       = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT / "static" / "uploads"

from backend.core.voice_query.voice_query_handler import VoiceQueryHandler

# In-memory handler cache  (replace with Redis in production)
active_handlers: Dict[str, VoiceQueryHandler] = {}


class VoiceQueryRequest(BaseModel):
    report_id: str
    query: str


class VoiceQueryResponse(BaseModel):
    report_id: str
    query: str
    answer: str
    data: Dict[str, Any]


def _get_handler(report_id: str) -> VoiceQueryHandler:
    """Load (or reuse) a VoiceQueryHandler for the given report_id."""
    if report_id not in active_handlers:
        files = list(UPLOAD_DIR.glob(f"{report_id}.*"))
        if not files:
            raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found. Upload a file first.")
        try:
            active_handlers[report_id] = VoiceQueryHandler(report_id, files[0])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading report: {e}")
    return active_handlers[report_id]


@router.post("/ask", response_model=VoiceQueryResponse, tags=["Voice Query"])
async def voice_query(request: VoiceQueryRequest):
    """
    Process a text / voice query against a previously uploaded report.

    Example queries:
      - "What is the total sales?"
      - "Show me top 5 by revenue"
      - "Any anomalies in profit?"
      - "Best category by sales"
      - "Dataset summary"
    """
    handler = _get_handler(request.report_id)
    try:
        result = handler.process_query(request.query)
        # If handler returned an error dict, raise 400
        if result.get("query_type") == "error":
            raise HTTPException(status_code=400, detail=result.get("error", "Query error"))
        return VoiceQueryResponse(
            report_id=request.report_id,
            query=request.query,
            answer=result.get("answer", "No answer available"),
            data=result.get("data", {}),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {e}")


@router.get("/suggestions/{report_id}", tags=["Voice Query"])
async def get_query_suggestions(report_id: str):
    """Return context-aware example queries based on the dataset's columns."""
    handler = _get_handler(report_id)
    suggestions = handler.get_suggestions()
    return {"report_id": report_id, "suggestions": suggestions}


@router.delete("/clear/{report_id}", tags=["Voice Query"])
async def clear_handler(report_id: str):
    """Free the in-memory handler for a report (call after session ends)."""
    if report_id in active_handlers:
        del active_handlers[report_id]
        return {"message": f"Handler for '{report_id}' cleared."}
    return {"message": f"No handler found for '{report_id}'."}


@router.get("/help", tags=["Voice Query"])
async def get_help():
    """Return supported query types with examples."""
    return {
        "supported_queries": [
            {"category": "Aggregations",
             "examples": ["total sales", "average profit", "maximum revenue", "minimum cost"]},
            {"category": "Top / Bottom",
             "examples": ["top 5 by sales", "bottom 10 by profit"]},
            {"category": "Trend",
             "examples": ["show revenue trend", "monthly sales trend"]},
            {"category": "Best / Worst Category",
             "examples": ["best category by sales", "worst product by profit"]},
            {"category": "Anomaly Detection",
             "examples": ["anomalies in revenue", "outliers in price"]},
            {"category": "Group By",
             "examples": ["sales grouped by category", "profit per region"]},
            {"category": "Correlation",
             "examples": ["correlation between sales and profit"]},
            {"category": "Distribution",
             "examples": ["distribution of price", "spread of revenue"]},
            {"category": "Data Quality",
             "examples": ["missing values", "how many duplicates", "unique values in category"]},
            {"category": "Summary",
             "examples": ["dataset summary", "describe the data"]},
        ]
    }
