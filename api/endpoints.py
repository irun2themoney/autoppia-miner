"""API endpoints"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from config.settings import settings
import os
import time
import logging
import asyncio

router = APIRouter()

# Shared advanced_metrics instance - must be created here so dashboard can access it
from api.utils.advanced_metrics import AdvancedMetrics
advanced_metrics = AdvancedMetrics()

# Initialize agent based on configuration
def get_agent():
    """Get agent instance based on settings"""
    agent_type = os.getenv("AGENT_TYPE", settings.agent_type).lower()
    
    # Always use hybrid (enhanced template agent)
    if agent_type in ["hybrid", "template"]:
        from .agent.hybrid import HybridAgent
        return HybridAgent()
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
    try:
        if http_request:
            # Try to get client IP from request (FastAPI stores it in client.host)
            if hasattr(http_request, 'client') and http_request.client:
                validator_ip = str(http_request.client.host) if http_request.client.host else None
            # Fallback to headers
            if not validator_ip:
                forwarded = http_request.headers.get("X-Forwarded-For")
                if forwarded:
                    validator_ip = forwarded.split(",")[0].strip()
                else:
                    validator_ip = http_request.headers.get("X-Real-IP")
            # Skip localhost - don't record local tests as validator activity
            if validator_ip in ["127.0.0.1", "localhost", "::1", None]:
                validator_ip = None
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.debug(f"Error extracting validator IP: {e}")
        validator_ip = None
    
    # Initialize task_type with default
    task_type = "generic"
    
    try:
        # Parse task for metrics (inside try block to catch errors)
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
    except Exception as e:
        # If parsing fails, use generic task type
        task_type = "generic"
    
    # Validate request
    if not request.id or not request.prompt:
        logger = logging.getLogger(__name__)
        logger.warning(f"Invalid request: missing id or prompt. ID: {request.id}, Prompt: {bool(request.prompt)}")
        return JSONResponse(
            content={
                "actions": [],
                "web_agent_id": request.id or "unknown",
                "recording": "",
                "id": request.id or "unknown",
                "task_id": request.id or "unknown",
            },
            status_code=400,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    try:
        # Solve task using agent with timeout protection (25 seconds max)
        # Pass validator_ip for god-tier features (validator learning)
        actions = await asyncio.wait_for(
            agent.solve_task(
                task_id=request.id,
                prompt=request.prompt,
                url=request.url,
                validator_ip=validator_ip if validator_ip else None
            ),
            timeout=25.0  # 25 second timeout to prevent hanging
        )
        
        response_time = time.time() - start_time
        
        # Only record in metrics if it's from a validator (not local test)
        if validator_ip:  # Only record validator requests, skip local tests
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
            
            # Also record in basic metrics (only for validators)
            from api.utils.metrics import metrics
            metrics.record_request(success=True, response_time=response_time, task_type=task_type)
            
            # GOD-TIER: Record for validator learning (if agent supports it)
            if hasattr(agent, 'record_validator_result'):
                try:
                    agent.record_validator_result(
                        validator_ip=validator_ip,
                        task_prompt=request.prompt,
                        task_url=request.url,
                        actions=actions,
                        success=True,  # We assume success if no error
                        response_time=response_time,
                        task_type=task_type,
                        score=None  # Score not available from validator yet
                    )
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Error recording validator result: {e}")
            
            # DYNAMIC ZERO: Track task diversity and anti-overfitting
            try:
                from api.utils.task_diversity import task_diversity
                from api.utils.anti_overfitting import anti_overfitting
                task_diversity.analyze_task_diversity(request.prompt, request.url)
            except Exception as e:
                logger.debug(f"Task diversity tracking failed: {e}")
        
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
    
    except asyncio.TimeoutError:
        # Handle timeout - return empty actions
        logger = logging.getLogger(__name__)
        logger.warning(f"Task {request.id} timed out after 25 seconds")
        
        response_time = time.time() - start_time
        from api.utils.metrics import metrics
        from api.endpoints import advanced_metrics
        
        # Only record in metrics if it's from a validator (not local test)
        if validator_ip:  # Only record validator requests, skip local tests
            metrics.record_request(success=False, response_time=response_time, task_type="timeout")
            advanced_metrics.record_request(
                success=False,
                response_time=response_time,
                task_type=task_type,
                agent_type=os.getenv("AGENT_TYPE", settings.agent_type),
                error_type="TimeoutError",
                validator_ip=validator_ip
            )
        
        return JSONResponse(
            content={
                "actions": [],
                "web_agent_id": request.id,
                "recording": "",
                "id": request.id,
                "task_id": request.id,
            },
            status_code=200,  # Return 200 with empty actions (not 500)
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
        
        logger = logging.getLogger(__name__)
        response_time = time.time() - start_time
        error_type = type(e).__name__
        error_message = str(e)
        
        # Log full error with traceback for debugging
        logger.error(
            f"Error processing task {request.id}: {error_type}: {error_message}\n"
            f"Traceback: {''.join(traceback.format_exc())}\n"
            f"Validator IP: {validator_ip}, Task: {request.prompt[:100]}..."
        )
        
        # Only record in metrics if it's from a validator (not local test)
        if validator_ip:  # Only record validator requests, skip local tests
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

