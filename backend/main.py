"""
FastAPI server for the competitive analysis web application.
This module provides REST API endpoints for the competitive analysis service.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import uuid
import asyncio
import logging
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import run_competitive_analysis
from pdf_generator import create_competitive_analysis_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Competitive Analysis API",
    description="AI-powered competitive analysis using LangChain and Google Gemini",
    version="1.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_dir = "/home/rabia/Documents/Langchain-Project/competitive-analysis-agent/frontend"
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Global storage for analysis results (in production, use a database)
analysis_results: Dict[str, Dict[str, Any]] = {}


class AnalysisRequest(BaseModel):
    """Request model for competitive analysis."""
    business_idea: str
    location: str


class AnalysisStatus(BaseModel):
    """Response model for analysis status."""
    id: str
    status: str
    progress: Optional[str] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint that serves the frontend."""
    frontend_path = "/home/rabia/Documents/Langchain-Project/competitive-analysis-agent/frontend/index.html"
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Competitive Analysis API", "docs": "/docs"}


@app.post("/api/analyze", response_model=Dict[str, str])
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start a competitive analysis process.
    
    Args:
        request: Analysis request containing business idea, location, and API key
        background_tasks: FastAPI background tasks for async processing
        
    Returns:
        Dictionary with analysis ID for tracking progress
    """
    try:
        # Validate input
        if not request.business_idea.strip():
            raise HTTPException(status_code=400, detail="Business idea is required")
        if not request.location.strip():
            raise HTTPException(status_code=400, detail="Location is required")
        
        # Get API key from environment
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured on server")
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Initialize analysis status
        analysis_results[analysis_id] = {
            'id': analysis_id,
            'status': 'started',
            'progress': 'Initializing analysis...',
            'business_idea': request.business_idea,
            'location': request.location,
            'created_at': datetime.now().isoformat(),
            'competitors': [],
            'analysis': '',
            'pdf_path': None
        }
        
        # Start background analysis
        background_tasks.add_task(
            run_analysis_background,
            analysis_id,
            request.business_idea,
            request.location,
            google_api_key
        )
        
        logger.info(f"Started analysis {analysis_id} for {request.business_idea} in {request.location}")
        
        return {"id": analysis_id, "status": "started"}
        
    except Exception as e:
        logger.error(f"Error starting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@app.get("/api/status/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """
    Get the status of a running analysis.
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        Current status and progress of the analysis
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        result = analysis_results[analysis_id]
        
        return AnalysisStatus(
            id=analysis_id,
            status=result['status'],
            progress=result.get('progress'),
            error=result.get('error'),
            completed_at=result.get('completed_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis status")


@app.get("/api/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """
    Get the complete results of a finished analysis.
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        Complete analysis results including competitors and insights
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        result = analysis_results[analysis_id]
        
        if result['status'] != 'completed':
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        return {
            'id': analysis_id,
            'business_idea': result['business_idea'],
            'location': result['location'],
            'competitors': result['competitors'],
            'analysis': result['analysis'],
            'created_at': result['created_at'],
            'completed_at': result['completed_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis results")


@app.get("/api/download/{analysis_id}")
async def download_pdf_report(analysis_id: str):
    """
    Download the PDF report for a completed analysis.
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        PDF file download response
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        result = analysis_results[analysis_id]
        
        if result['status'] != 'completed':
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        pdf_path = result.get('pdf_path')
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF report not found")
        
        # Generate a user-friendly filename
        business_name = result['business_idea'].replace(' ', '_')[:20]
        location_name = result['location'].replace(' ', '_')[:15]
        filename = f"competitive_analysis_{business_name}_{location_name}.pdf"
        
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download PDF report")


async def run_analysis_background(analysis_id: str, business_idea: str, 
                                location: str, google_api_key: str):
    """
    Background task to run the competitive analysis.
    
    Args:
        analysis_id: Unique identifier for the analysis
        business_idea: The business idea to research
        location: Target location for the business
        google_api_key: Google API key for Gemini
    """
    try:
        logger.info(f"Running background analysis {analysis_id}")
        
        # Update status
        analysis_results[analysis_id]['status'] = 'searching'
        analysis_results[analysis_id]['progress'] = 'Searching for competitors...'
        
        # Run the competitive analysis
        results = run_competitive_analysis(business_idea, location, google_api_key)
        
        if results['status'] == 'error':
            analysis_results[analysis_id]['status'] = 'failed'
            analysis_results[analysis_id]['error'] = results['error']
            return
        
        # Update status
        analysis_results[analysis_id]['status'] = 'analyzing'
        analysis_results[analysis_id]['progress'] = 'Analyzing competitor data...'
        
        # Store the results
        analysis_results[analysis_id]['competitors'] = results['competitors']
        analysis_results[analysis_id]['analysis'] = results['analysis']
        
        # Update status
        analysis_results[analysis_id]['status'] = 'generating_pdf'
        analysis_results[analysis_id]['progress'] = 'Generating PDF report...'
        
        # Generate PDF report
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_path = create_competitive_analysis_report(
            business_idea=business_idea,
            location=location,
            competitors=results['competitors'],
            analysis=results['analysis'],
            output_dir=reports_dir
        )
        
        # Final update
        analysis_results[analysis_id]['status'] = 'completed'
        analysis_results[analysis_id]['progress'] = 'Analysis completed successfully!'
        analysis_results[analysis_id]['pdf_path'] = pdf_path
        analysis_results[analysis_id]['completed_at'] = datetime.now().isoformat()
        
        logger.info(f"Completed analysis {analysis_id}")
        
    except Exception as e:
        logger.error(f"Error in background analysis {analysis_id}: {str(e)}")
        analysis_results[analysis_id]['status'] = 'failed'
        analysis_results[analysis_id]['error'] = str(e)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
