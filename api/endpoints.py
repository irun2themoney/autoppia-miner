"""API endpoints"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from config.settings import settings
import os
import time

router = APIRouter()

# Shared advanced_metrics instance - must be created here so dashboard can access it
from api.utils.advanced_metrics import AdvancedMetrics
advanced_metrics = AdvancedMetrics()

# Initialize agent based on configuration
def get_agent():
    """Get agent instance based on settings"""
    agent_type = os.getenv("AGENT_TYPE", settings.agent_type).lower()
    
    if agent_type == "hybrid":
        from .agent.hybrid import HybridAgent
        return HybridAgent()
    elif agent_type == "chutes":
        from .agent.chutes import ChutesAgent
        return ChutesAgent()
    else:
        from .agent.template import TemplateAgent
        return TemplateAgent()

agent = get_agent()


class TaskRequest(BaseModel):
    id: str
    prompt: str
    url: str


class TaskResponse(BaseModel):
    actions: List[Dict[str, Any]]
    web_agent_id: str
    recording: str
    id: str
    task_id: str


@router.options("/solve_task")
async def solve_task_options():
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        }
    )


@router.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    from ..utils.metrics import metrics
    return JSONResponse(
        content=metrics.get_metrics(),
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.post("/solve_task")
async def solve_task(request: TaskRequest, http_request: Request):
    """
    Main endpoint - matches ApifiedWebAgent expectations
    Input: task.clean_task() format
    Output: {actions: [], web_agent_id: str, recording: str}
    """
    from api.endpoints import advanced_metrics  # Use shared instance
    from api.utils.task_parser import TaskParser
    
    start_time = time.time()
    validator_ip = None
    
    # Get validator IP if available
    validator_ip = None
    try:
        if http_request:
            # Try to get client IP from request
            if hasattr(http_request, 'client') and http_request.client:
                validator_ip = getattr(http_request.client, 'host', None)
            # Fallback to headers
            if not validator_ip:
                forwarded = http_request.headers.get("X-Forwarded-For")
                if forwarded:
                    validator_ip = forwarded.split(",")[0].strip()
                else:
                    validator_ip = http_request.headers.get("X-Real-IP")
    except Exception as e:
        pass
    
    # Parse task for metrics
    task_parser = TaskParser()
    parsed_task = task_parser.parse_task(request.prompt, request.url)
    # Determine task type from parsed task
    if parsed_task.get("has_login"):
        task_type = "login"
    elif parsed_task.get("has_form"):
        task_type = "form"
    elif parsed_task.get("has_search"):
        task_type = "search"
    elif parsed_task.get("has_modify"):
        task_type = "modify"
    else:
        task_type = "generic"
    
    try:
        # Solve task using agent
        actions = await agent.solve_task(
            task_id=request.id,
            prompt=request.prompt,
            url=request.url
        )
        
        response_time = time.time() - start_time
        
        # Record success in advanced metrics
        advanced_metrics.record_request(
            success=True,
            response_time=response_time,
            task_type=task_type,
            agent_type=os.getenv("AGENT_TYPE", settings.agent_type),
            validator_ip=validator_ip,
            cache_hit=False,  # Will be enhanced later
            vector_recall=False,  # Will be enhanced later
            mutation_detected=False  # Will be enhanced later
        )
        
        # Also record in basic metrics
        from api.utils.metrics import metrics
        metrics.record_request(success=True, response_time=response_time, task_type=task_type)
        
        return JSONResponse(
            content={
                "actions": actions,
                "web_agent_id": request.id,
                "recording": "",
                "id": request.id,
                "task_id": request.id,
            },
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    except Exception as e:
        # Record error in metrics
        from api.utils.metrics import metrics
        from api.endpoints import advanced_metrics  # Use shared instance
        import traceback
        
        response_time = time.time() - start_time
        error_type = type(e).__name__
        
        metrics.record_request(success=False, response_time=response_time, task_type="error")
        
        # Record in advanced metrics
        advanced_metrics.record_request(
            success=False,
            response_time=response_time,
            task_type=task_type,
            agent_type=os.getenv("AGENT_TYPE", settings.agent_type),
            error_type=error_type,
            validator_ip=validator_ip
        )
        
        # Return empty actions on error (playground expects this)
        return JSONResponse(
            content={
                "actions": [],
                "web_agent_id": request.id,
                "recording": "",
                "id": request.id,
                "task_id": request.id,
            },
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

