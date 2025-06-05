from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os
from dotenv import load_dotenv

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from sentiment_analyzer import SentimentAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    print(f"Files in parent directory: {os.listdir('..')}")
    raise

app = FastAPI(title="Advanced Sentiment Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the sentiment analyzer
analyzer = SentimentAnalyzer()

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str  # "sentiment" or "comparison"

class AttributeComparison(BaseModel):
    object1: str
    object2: str
    attributes: Dict[str, Dict[str, float]]

class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float
    implications: Optional[List[str]] = None
    comparison: Optional[AttributeComparison] = None
    explanation: str

@app.get("/")
async def root():
    return {"message": "Sentiment Analysis API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    try:
        if request.analysis_type == "sentiment":
            # Single text sentiment analysis
            result = analyzer.analyze(request.text)
            return AnalysisResponse(
                sentiment=result["sentiment"],
                confidence=result["confidence"],
                implications=result.get("implications", []),
                explanation=result["explanation"]
            )
        elif request.analysis_type == "comparison":
            # Comparison analysis
            result = analyzer.analyze(request.text)
            return AnalysisResponse(
                sentiment=result["sentiment"],
                confidence=result["confidence"],
                comparison=result["comparison"],
                explanation=result["explanation"]
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=3000,
        reload=True,
        ssl_keyfile=None,
        ssl_certfile=None,
        log_level="info"
    ) 