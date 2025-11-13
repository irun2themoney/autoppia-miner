"""
API server for Autoppia Worker
This provides an HTTP API interface for the worker to integrate with Autoppia infrastructure
"""

import json
from typing import Dict, Any
from datetime import datetime, timezone
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

# Configure CORS more securely
import os
cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize worker
worker = AutoppiaWorker()

# Request tracking for metrics
class RequestMetrics:
    def __init__(self):
        self.total_requests = 0
        self.total_errors = 0
        self.total_success = 0
    
metrics = RequestMetrics()


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


def _generate_default_actions(url: str, prompt: str) -> list:
    """Generate default action sequence as fallback"""
    actions = []
    
    if url:
        actions.append({
            "action_type": "navigate",
            "url": url
        })
    
    actions.append({
        "action_type": "wait",
        "duration": 2.0
    })
    
    actions.append({
        "action_type": "screenshot"
    })
    
    return actions


@app.post("/solve_task")
async def solve_task(request_data: Dict[str, Any]):
    """
    Solve task endpoint for Autoppia mining
    This endpoint is called by the miner to solve web agent tasks
    
    Request format:
    {
        "id": "task_id",
        "prompt": "Task description",
        "url": "https://example.com",
        "seed": 12345,
        "web_project_name": "project_name",
        "specifications": {...}
    }
    
    Response format:
    {
        "task_id": "task_id",
        "actions": [
            {"action_type": "click", "x": 100, "y": 100},
            {"action_type": "type", "text": "hello", "selector": "#input"}
        ],
        "success": true,
        "message": "Task processed successfully"
    }
    """
    metrics.total_requests += 1
    try:
        task_id = request_data.get("id", "unknown")
        prompt = request_data.get("prompt", "")
        url = request_data.get("url", "")
        
        logger.info(f"Received task: {task_id}")
        logger.debug(f"Task prompt: {prompt}")
        logger.debug(f"Task URL: {url}")
        
        if not prompt:
            logger.warning(f"Task {task_id} has no prompt")
            metrics.total_errors += 1
            return JSONResponse(
                content={
                    "task_id": task_id,
                    "success": False,
                    "error": "No prompt provided",
                    "actions": []
                },
                status_code=400
            )
        
        # Use AI to generate action sequence
        # Create a specialized prompt for web agent action generation
        ai_prompt = f"""You are a web automation expert. Analyze this task and generate a sequence of browser actions.

Task: {prompt}
URL: {url if url else 'Not specified'}

Generate actions as a JSON array. Each action should have:
- action_type: 'navigate', 'click', 'type', 'wait', 'screenshot', 'scroll', 'select', 'hover'
- Additional fields based on action type (url, x, y, text, selector, duration, direction)

Return ONLY valid JSON array, no markdown or explanation.
Example: [
  {{"action_type": "navigate", "url": "https://example.com"}},
  {{"action_type": "wait", "duration": 2}},
  {{"action_type": "screenshot"}}
]"""
        
        # Call worker to generate actions via AI
        gen_request = WorkerRequest(
            task="generate",
            input_data={
                "prompt": ai_prompt,
                "max_tokens": 2000,
                "temperature": 0.3
            }
        )
        
        gen_response = await worker.process(gen_request)
        
        actions = []
        if gen_response.success and gen_response.result:
            try:
                # Try to parse generated actions from AI response
                generated_text = gen_response.result.get("generated_text", "")
                
                # Try to extract JSON from response
                import json
                if "[" in generated_text and "]" in generated_text:
                    json_start = generated_text.index("[")
                    json_end = generated_text.rindex("]") + 1
                    json_str = generated_text[json_start:json_end]
                    actions = json.loads(json_str)
                    logger.info(f"Generated {len(actions)} actions via AI for task {task_id}")
                else:
                    logger.warning(f"Could not parse AI response for task {task_id}")
                    # Fall back to default actions
                    actions = _generate_default_actions(url, prompt)
            except Exception as e:
                logger.warning(f"Error parsing AI actions: {str(e)}, using defaults")
                actions = _generate_default_actions(url, prompt)
        else:
            logger.warning(f"AI generation failed for task {task_id}, using default actions")
            actions = _generate_default_actions(url, prompt)
        
        response = {
            "task_id": task_id,
            "actions": actions,
            "success": True,
            "message": f"Task processed successfully with {len(actions)} actions"
        }
        
        metrics.total_success += 1
        logger.info(f"Task {task_id} completed: {len(actions)} actions")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Error solving task: {str(e)}")
        task_id = request_data.get("id", "unknown") if isinstance(request_data, dict) else "unknown"
        metrics.total_errors += 1
        return JSONResponse(
            content={
                "task_id": task_id,
                "success": False,
                "error": str(e),
                "actions": []
            },
            status_code=500
        )


@app.get("/metrics")
async def get_metrics():
    """Get worker metrics for monitoring"""
    import time
    import os
    
    # Get worker uptime (would need to track in production)
    try:
        start_time = float(os.getenv("WORKER_START_TIME", time.time()))
        uptime_seconds = int(time.time() - start_time)
        uptime_str = f"{uptime_seconds}s"
    except:
        uptime_str = "unknown"
    
    # Return comprehensive metrics including request tracking
    return {
        "worker": worker.worker_name,
        "version": worker.worker_version,
        "status": "operational",
        "uptime": uptime_str,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chutes_api_configured": worker.config.chutes_api_key is not None,
        "capabilities": worker.get_metadata().get("capabilities", []),
        "requests": {
            "total": metrics.total_requests,
            "success": metrics.total_success,
            "errors": metrics.total_errors
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (Railway/Render set this)
    port = int(os.getenv("PORT", 8080))
    
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

