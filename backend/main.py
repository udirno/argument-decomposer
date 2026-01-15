"""FastAPI application for Multi-Perspective Debate Explorer."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from agents import analyze_question
import uvicorn

app = FastAPI(title="Multi-Perspective Debate Explorer", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"message": "Multi-Perspective Debate Explorer API", "status": "running"}


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
    try:
        perspectives = await analyze_question(request.question)
        
        return AnalysisResponse(
            perspectives=[
                PerspectiveResponse(**p) for p in perspectives
            ]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

