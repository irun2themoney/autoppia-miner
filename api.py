"""
API server for Autoppia Worker
This provides an HTTP API interface for the worker to integrate with Autoppia infrastructure
"""

import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from worker import AutoppiaWorker, WorkerRequest, WorkerResponse
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Autoppia Miner Worker",
    description="An Autoppia AI Worker for mining and processing tasks",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize worker
worker = AutoppiaWorker()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "autoppia-miner",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Autoppia infrastructure"""
    try:
        health = await worker.health_check()
        return JSONResponse(content=health)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/metadata")
async def get_metadata():
    """Get worker metadata"""
    try:
        metadata = worker.get_metadata()
        return JSONResponse(content=metadata)
    except Exception as e:
        logger.error(f"Failed to get metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_request(request_data: Dict[str, Any]):
    """
    Process a worker request
    
    Request body should contain:
    - task: Task type (mine, process, generate)
    - input_data: Input data for the task
    - parameters: Optional additional parameters
    """
    try:
        # Validate request
        if "task" not in request_data:
            raise HTTPException(status_code=400, detail="Missing 'task' field")
        
        # Create WorkerRequest
        worker_request = WorkerRequest(
            task=request_data["task"],
            input_data=request_data.get("input_data"),
            parameters=request_data.get("parameters")
        )
        
        # Process request
        response = await worker.process(worker_request)
        
        # Return response
        return JSONResponse(content=response.dict())
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get worker metrics for monitoring"""
    # Placeholder for metrics endpoint
    return {
        "requests_processed": 0,
        "errors": 0,
        "uptime": "0s"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

