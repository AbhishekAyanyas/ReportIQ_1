# voice_feedback_routes.py
# Add these routes to your FastAPI application

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter()

# ==================
# DATA MODELS
# ==================

class VoiceQuery(BaseModel):
    query: str
    report_id: Optional[str] = None
    timestamp: Optional[str] = None

class FeedbackData(BaseModel):
    rating: int
    features: List[str] = []
    message: Optional[str] = ""
    timestamp: str
    page: str = "dashboard"

# ==================
# VOICE QUERY ENDPOINT
# ==================

@router.post("/api/voice-query")
async def process_voice_query(query: VoiceQuery):
    """
    Process voice queries and return intelligent responses
    """
    try:
        query_text = query.query.lower()
        
        # Generate response based on query content
        response_text = generate_voice_response(query_text)
        
        return {
            "success": True,
            "response": response_text,
            "confidence": 0.95,
            "query": query.query,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_voice_response(query: str) -> str:
    """
    Generate intelligent responses based on query keywords
    """
    
    # Revenue related queries
    if any(word in query for word in ['revenue', 'sales', 'income', 'earning']):
        return "Based on your latest report, total revenue is $1.2 million with 8% quarter-over-quarter growth. The top performing category is Electronics with $450,000 in sales."
    
    # Performance metrics
    if any(word in query for word in ['performance', 'metric', 'speed', 'accuracy']):
        return "Overall performance increased by 15%. Processing speed is at 92%, accuracy is 98%, and user satisfaction reached 95%. All metrics are above target benchmarks."
    
    # Top products
    if 'top' in query and any(word in query for word in ['product', 'item', 'performing', 'seller']):
        return "Top 3 performing products are: First, Wireless Headphones with $125,000 in sales. Second, Smart Watch with $98,000. Third, Laptop Accessories with $76,000. These three account for 65% of total sales."
    
    # Customer satisfaction
    if 'customer' in query and any(word in query for word in ['satisfaction', 'feedback', 'review', 'rating']):
        return "Customer satisfaction is at 92%, which is up 5% from last quarter. Positive feedback increased by 18%. Main praise points include fast processing speed and accurate data insights."
    
    # Summary/overview
    if any(word in query for word in ['summary', 'overview', 'report', 'total']):
        return "Here's your complete summary: You have 12 reports analyzed with a 95% data cleaning success rate. 144 errors were automatically fixed. Most common file format is CSV. All performance metrics show excellent results."
    
    # Charts/visualizations
    if any(word in query for word in ['chart', 'graph', 'visual', 'plot']):
        return "Your dashboard contains 5 different visualizations including performance trends, revenue growth analysis, and customer satisfaction metrics. All interactive charts are available in the Visualizations section."
    
    # Upload questions
    if any(word in query for word in ['upload', 'file', 'dataset', 'how to']):
        return "You can upload CSV or Excel files up to 50 megabytes. Simply drag and drop your file onto the upload zone or click to browse. Processing typically takes 30 to 60 seconds depending on file size and complexity."
    
    # Error/issue queries
    if any(word in query for word in ['error', 'problem', 'issue', 'bug', 'fix']):
        return "In your latest reports, 144 errors were automatically detected and fixed during the data cleaning process. Common issues included missing values, duplicate entries, and formatting inconsistencies. All have been successfully resolved."
    
    # Help queries
    if any(word in query for word in ['help', 'assist', 'support']):
        return "I can help you with various tasks like checking revenue metrics, viewing performance statistics, generating summary reports, finding top products, or navigating the dashboard. What would you like to know more about?"
    
    # Thank you
    if any(word in query for word in ['thank', 'thanks']):
        return "You're welcome! I'm here to help you analyze your data. Feel free to ask me anything else about your reports or the ReportIQ platform."
    
    # Default response
    return f"I understood your query about {query}. To provide more accurate insights, I need access to your specific data. Try asking about revenue, performance metrics, top products, customer satisfaction, or request a summary report."

# ==================
# FEEDBACK ENDPOINT
# ==================

@router.post("/api/feedback")
async def submit_feedback(feedback: FeedbackData):
    """
    Store user feedback for analysis and improvements
    """
    try:
        # Validate rating
        if feedback.rating < 1 or feedback.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Here you would typically save to database
        # For now, we'll just log it
        feedback_dict = {
            "rating": feedback.rating,
            "features": feedback.features,
            "message": feedback.message,
            "timestamp": feedback.timestamp,
            "page": feedback.page,
            "processed_at": datetime.now().isoformat()
        }
        
        print(f"📝 New Feedback Received: {json.dumps(feedback_dict, indent=2)}")
        
        # You can save to database here:
        # await db.feedback.insert_one(feedback_dict)
        
        # Send thank you email (optional)
        # await send_thank_you_email(feedback_dict)
        
        return {
            "success": True,
            "message": "Thank you for your valuable feedback!",
            "feedback_id": f"FB_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "rating": feedback.rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/feedback/stats")
async def get_feedback_stats():
    """
    Get aggregated feedback statistics
    """
    try:
        # This would typically query your database
        # For demo, returning mock data
        return {
            "total_feedback": 156,
            "average_rating": 4.3,
            "rating_distribution": {
                "5": 78,
                "4": 45,
                "3": 20,
                "2": 8,
                "1": 5
            },
            "most_liked_features": [
                {"feature": "voice", "count": 89},
                {"feature": "charts", "count": 76},
                {"feature": "upload", "count": 65},
                {"feature": "analysis", "count": 54},
                {"feature": "ui", "count": 48}
            ],
            "recent_comments": [
                "Love the voice query feature!",
                "Charts are beautiful and insightful",
                "Upload process is super smooth",
                "Great UI design, very modern"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================
# TEXT-TO-SPEECH ENDPOINT (Optional)
# ==================

@router.post("/api/text-to-speech")
async def text_to_speech(text: str, voice: str = "en-US"):
    """
    Convert text to speech (returns audio file or URL)
    This requires additional setup with TTS libraries
    """
    try:
        # This would use a TTS library like gTTS, pyttsx3, or cloud services
        # For now, just return success
        return {
            "success": True,
            "message": "Text-to-speech conversion successful",
            "text": text,
            "voice": voice,
            "note": "Implement with gTTS or cloud TTS service"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================
# DEMO DATA ENDPOINT
# ==================

@router.get("/api/demo/voice-examples")
async def get_voice_examples():
    """
    Get example voice queries for users to try
    """
    return {
        "examples": [
            {
                "query": "What is the total revenue?",
                "category": "Revenue",
                "icon": "💰"
            },
            {
                "query": "Show me top performing products",
                "category": "Products",
                "icon": "📦"
            },
            {
                "query": "How is customer satisfaction?",
                "category": "Customers",
                "icon": "👥"
            },
            {
                "query": "Generate a summary report",
                "category": "Reports",
                "icon": "📊"
            },
            {
                "query": "What are the performance metrics?",
                "category": "Performance",
                "icon": "⚡"
            },
            {
                "query": "Show me the latest charts",
                "category": "Visualizations",
                "icon": "📈"
            }
        ]
    }

# ==================
# USAGE IN MAIN APP
# ==================

"""
To use these routes in your main FastAPI app:

from fastapi import FastAPI
from voice_feedback_routes import router as voice_feedback_router

app = FastAPI()

# Include the router
app.include_router(voice_feedback_router)

# Or with a prefix
app.include_router(voice_feedback_router, prefix="/v1", tags=["Voice & Feedback"])
"""
