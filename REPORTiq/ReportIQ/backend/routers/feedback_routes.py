from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime
from typing import Optional, List

router = APIRouter()

ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_DIR = ROOT / "static" / "feedback"
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic models
class FeedbackCreate(BaseModel):
    report_id: str
    rating: int  # 1-5 stars
    comment: str
    category: Optional[str] = "general"  # general, bug, suggestion, praise

class FeedbackResponse(BaseModel):
    feedback_id: str
    report_id: str
    rating: int
    comment: str
    category: str
    timestamp: str


@router.post("/submit", tags=["Feedback"], response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackCreate):
    """Submit feedback for a report"""
    
    # Validate rating
    if feedback.rating < 1 or feedback.rating > 5:
        raise HTTPException(400, "Rating must be between 1 and 5")
    
    # Generate feedback ID
    feedback_id = f"{feedback.report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create feedback data
    feedback_data = {
        "feedback_id": feedback_id,
        "report_id": feedback.report_id,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "category": feedback.category,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to JSON file
    feedback_file = FEEDBACK_DIR / f"{feedback_id}.json"
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, indent=2, ensure_ascii=False)
    
    return feedback_data


@router.get("/report/{report_id}", tags=["Feedback"])
async def get_report_feedback(report_id: str):
    """Get all feedback for a specific report"""
    
    feedbacks = []
    
    # Read all feedback files for this report
    for feedback_file in FEEDBACK_DIR.glob(f"{report_id}_*.json"):
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                feedback_data = json.load(f)
                feedbacks.append(feedback_data)
        except Exception as e:
            print(f"Error reading feedback file {feedback_file}: {e}")
    
    # Sort by timestamp (newest first)
    feedbacks.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return {
        "report_id": report_id,
        "total_feedbacks": len(feedbacks),
        "average_rating": sum(f['rating'] for f in feedbacks) / len(feedbacks) if feedbacks else 0,
        "feedbacks": feedbacks
    }


@router.get("/all", tags=["Feedback"])
async def get_all_feedback():
    """Get all feedback from all reports"""
    
    feedbacks = []
    
    # Read all feedback files
    for feedback_file in FEEDBACK_DIR.glob("*.json"):
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                feedback_data = json.load(f)
                feedbacks.append(feedback_data)
        except Exception as e:
            print(f"Error reading feedback file {feedback_file}: {e}")
    
    # Sort by timestamp (newest first)
    feedbacks.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Calculate statistics
    total_feedbacks = len(feedbacks)
    average_rating = sum(f['rating'] for f in feedbacks) / total_feedbacks if feedbacks else 0
    
    # Count by category
    category_counts = {}
    for feedback in feedbacks:
        category = feedback.get('category', 'general')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Count by rating
    rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for feedback in feedbacks:
        rating = feedback.get('rating', 0)
        if rating in rating_counts:
            rating_counts[rating] += 1
    
    return {
        "total_feedbacks": total_feedbacks,
        "average_rating": round(average_rating, 2),
        "category_counts": category_counts,
        "rating_counts": rating_counts,
        "recent_feedbacks": feedbacks[:10]  # Last 10 feedbacks
    }


@router.delete("/delete/{feedback_id}", tags=["Feedback"])
async def delete_feedback(feedback_id: str):
    """Delete a specific feedback"""
    
    feedback_file = FEEDBACK_DIR / f"{feedback_id}.json"
    
    if not feedback_file.exists():
        raise HTTPException(404, "Feedback not found")
    
    try:
        feedback_file.unlink()
        return {
            "success": True,
            "message": "Feedback deleted successfully",
            "feedback_id": feedback_id
        }
    except Exception as e:
        raise HTTPException(500, f"Error deleting feedback: {str(e)}")
