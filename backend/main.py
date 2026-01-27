"""FastAPI application for Multi-Perspective Debate Explorer."""
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agents import analyze_question
from config import ALLOWED_ORIGINS, ENV
import uvicorn

logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Perspective Debate Explorer", version="1.0.0")

# CORS Configuration - restricted to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Configured via environment variable
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # Only allow needed methods
    allow_headers=["Content-Type"],  # Only allow needed headers
)

logger.info(f"Starting application in {ENV} mode with CORS origins: {ALLOWED_ORIGINS}")


class QuestionRequest(BaseModel):
    """Request model for question analysis."""
    question: str = Field(..., min_length=1, description="The ethical question to analyze")


class PerspectiveResponse(BaseModel):
    """Response model for a single perspective."""
    perspective: str
    analysis: str
    status: str


class AnalysisResponse(BaseModel):
    """Response model for the analysis endpoint."""
    perspectives: list[PerspectiveResponse]


@app.get("/")
async def root():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {
        "message": "Multi-Perspective Debate Explorer API",
        "status": "running",
        "version": "1.0.0",
        "environment": ENV
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: QuestionRequest):
    """
    Analyze an ethical question from 4 different perspectives.

    Returns analyses from:
    - Utilitarian perspective
    - Deontological perspective
    - Practical perspective
    - Stakeholder perspective
    """
    logger.info(f"Analysis requested for question: {request.question[:100]}...")

    try:
        perspectives = await analyze_question(request.question)

        logger.info(f"Analysis completed successfully with {len(perspectives)} perspectives")

        return AnalysisResponse(
            perspectives=[
                PerspectiveResponse(**p) for p in perspectives
            ]
        )
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while analyzing the question. Please try again."
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

