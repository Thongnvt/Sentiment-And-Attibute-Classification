from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os
import traceback
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logger.info(f"Current directory: {current_dir}")
logger.info(f"Parent directory: {parent_dir}")
logger.info(f"Python path: {sys.path}")

try:
    from sentiment_analyzer import SentimentAnalyzer
    logger.info("Successfully imported SentimentAnalyzer")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error(f"Python path: {sys.path}")
    logger.error(f"Current directory: {os.getcwd()}")
    logger.error(f"Files in current directory: {os.listdir('.')}")
    logger.error(f"Files in parent directory: {os.listdir('..')}")
    raise

app = FastAPI(title="Advanced Sentiment Analysis API")

# Configure CORS with specific origins
origins = [
    "http://localhost:3000",  # Frontend development server
    "http://localhost:3001",  # Backend server
    "https://frontend-omega-six-86.vercel.app",
    "https://*.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the sentiment analyzer
try:
    analyzer = SentimentAnalyzer()
    logger.info("Successfully initialized SentimentAnalyzer")
except Exception as e:
    logger.error(f"Error initializing SentimentAnalyzer: {e}")
    logger.error(traceback.format_exc())
    raise

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

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    try:
        logger.info(f"Received request: {request}")
        
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
        if request.analysis_type == "sentiment":
            # Single text sentiment analysis
            logger.info(f"Analyzing sentiment for text: {request.text}")
            try:
                result = analyzer.analyze(request.text)
                logger.info(f"Analysis result: {result}")
                return AnalysisResponse(
                    sentiment=result["sentiment"],
                    confidence=result["confidence"],
                    implications=result.get("implications", []),
                    explanation=result["explanation"]
                )
            except Exception as e:
                logger.error(f"Error in sentiment analysis: {e}")
                logger.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Error in sentiment analysis: {str(e)}")
                
        elif request.analysis_type == "comparison":
            # Comparison analysis
            logger.info(f"Analyzing comparison for text: {request.text}")
            try:
                result = analyzer.analyze(request.text)
                logger.info(f"Analysis result: {result}")
                return AnalysisResponse(
                    sentiment=result["sentiment"],
                    confidence=result["confidence"],
                    comparison=result["comparison"],
                    explanation=result["explanation"]
                )
            except Exception as e:
                logger.error(f"Error in comparison analysis: {e}")
                logger.error(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"Error in comparison analysis: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# For Vercel serverless deployment
if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=3001,
            reload=True,
            ssl_keyfile=None,
            ssl_certfile=None,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        logger.error(traceback.format_exc()) 