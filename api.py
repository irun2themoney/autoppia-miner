"""
API server for Autoppia Worker
This provides an HTTP API interface for the worker to integrate with Autoppia infrastructure

Enhanced with:
- Task Classification Engine (categorizes IWA tasks)
- Smart Action Generation (specialized templates per task type)
- Request Caching (reduces AI calls for similar tasks)
- Retry Logic (exponential backoff on failures)
"""

import json
import os
import re
import hashlib
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from collections import defaultdict
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from dotenv import load_dotenv
from worker import AutoppiaWorker, WorkerRequest

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Autoppia Miner Worker",
    description="Autoppia AI Worker for mining and processing tasks",
    version="0.1.0"
)
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
        self.by_type = defaultdict(int)  # Track by task type
        self.by_type_success = defaultdict(int)
    
metrics = RequestMetrics()


# Task Classification Engine
class TaskClassifier:
    """
    Intelligent task classifier for IWA tasks
    Categorizes tasks and provides specialized action generation
    """
    
    # Task type patterns
    PATTERNS = {
        "search": r"(search|find|look for|query|browse)",
        "form_fill": r"(fill|submit|complete|form|input|register)",
        "price_compare": r"(compare|price|cost|cheaper|expensive|discount|save)",
        "click": r"(click|select|choose|pick|tap)",
        "extract": r"(extract|get|retrieve|copy|collect|scrape)",
        "navigate": r"(go to|visit|open|access|navigate)",
        "scroll": r"(scroll|down|up|bottom|top|view more)",
        "checkout": r"(checkout|purchase|buy|add to cart|pay)"
    }
    
    @staticmethod
    def classify_task(prompt: str) -> str:
        """Classify task based on prompt keywords"""
        prompt_lower = prompt.lower()
        
        # Score each category
        scores = {}
        for task_type, pattern in TaskClassifier.PATTERNS.items():
            matches = len(re.findall(pattern, prompt_lower))
            scores[task_type] = matches
        
        # Return highest scoring category
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "generic"
    
    @staticmethod
    def generate_specialized_actions(task_type: str, url: str, prompt: str) -> List[Dict]:
        """Generate specialized action sequences based on task type"""
        
        actions = []
        
        # Navigate to URL first
        if url:
            actions.append({
                "action_type": "navigate",
                "url": url
            })
            actions.append({
                "action_type": "wait",
                "duration": 1.5
            })
        
        # Task-specific action templates
        if task_type == "search":
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.5},
                {"action_type": "click", "selector": "input[type='search'], input[placeholder*='search' i], .search-box"},
                {"action_type": "type", "text": "search query"},
                {"action_type": "key_press", "key": "Enter"},
                {"action_type": "wait", "duration": 2},
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "form_fill":
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.5},
                {"action_type": "click", "selector": "input:first-of-type"},
                {"action_type": "type", "text": "input_value"},
                {"action_type": "click", "selector": "button[type='submit'], .submit-btn"},
                {"action_type": "wait", "duration": 2},
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "price_compare":
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "scroll", "direction": "down", "amount": 3},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"},
                {"action_type": "scroll", "direction": "down", "amount": 3},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "click":
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.5},
                {"action_type": "click", "selector": "button:first-of-type, a.cta, [role='button']"},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "extract":
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "scroll", "direction": "down", "amount": 2},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"},
                {"action_type": "scroll", "direction": "down", "amount": 2},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "checkout":
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "click", "selector": "button[class*='cart'], .add-to-cart, .checkout"},
                {"action_type": "wait", "duration": 1.5},
                {"action_type": "screenshot"},
                {"action_type": "scroll", "direction": "down", "amount": 2},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"}
            ])
        
        else:  # generic
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 1},
                {"action_type": "scroll", "direction": "down", "amount": 2},
                {"action_type": "wait", "duration": 1},
                {"action_type": "screenshot"}
            ])
        
        return actions


# Request caching to reduce AI calls
class RequestCache:
    """Simple in-memory cache for task solutions"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get_key(self, prompt: str, url: str) -> str:
        """Generate cache key from prompt and URL"""
        combined = f"{prompt}:{url}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, prompt: str, url: str) -> Optional[List[Dict]]:
        """Retrieve cached actions"""
        key = self.get_key(prompt, url)
        if key in self.cache:
            cached, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.info(f"Cache hit for task")
                return cached
            else:
                del self.cache[key]
        return None
    
    def set(self, prompt: str, url: str, actions: List[Dict]) -> None:
        """Store actions in cache"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        key = self.get_key(prompt, url)
        self.cache[key] = (actions, time.time())
        logger.debug(f"Cached actions for task")


cache = RequestCache()


# Retry logic with exponential backoff
class RetryHandler:
    """Handle retries with exponential backoff"""
    
    @staticmethod
    async def call_with_retry(
        coro_func,
        max_retries: int = 3,
        base_delay: float = 0.5
    ):
        """Execute async function with retry logic"""
        import asyncio
        for attempt in range(max_retries):
            try:
                return await coro_func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                await asyncio.sleep(delay)



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
    Enhanced solve_task endpoint with task classification and smart action generation
    
    Features:
    - Task Classification (8 categories: search, form_fill, price_compare, etc.)
    - Specialized Action Generation (templates per task type)
    - Request Caching (reduces AI calls for similar tasks)
    - Retry Logic (handles transient failures gracefully)
    
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
        "task_type": "search|form_fill|price_compare|click|extract|checkout|navigate|scroll|generic",
        "actions": [...],
        "success": true,
        "cached": false,
        "message": "..."
    }
    """
    metrics.total_requests += 1
    start_time = time.time()
    
    try:
        task_id = request_data.get("id", "unknown")
        prompt = request_data.get("prompt", "")
        url = request_data.get("url", "")
        
        logger.info(f"📥 Received task: {task_id}")
        logger.debug(f"Task prompt: {prompt[:100]}...")
        logger.debug(f"Task URL: {url}")
        
        if not prompt:
            logger.warning(f"❌ Task {task_id} has no prompt")
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
        
        # Step 1: Classify the task
        task_type = TaskClassifier.classify_task(prompt)
        metrics.by_type[task_type] += 1
        logger.info(f"🏷️  Classified as: {task_type}")
        
        # Step 2: Check cache first (fast path)
        cached_actions = cache.get(prompt, url)
        if cached_actions:
            elapsed = time.time() - start_time
            response = {
                "task_id": task_id,
                "task_type": task_type,
                "actions": cached_actions,
                "success": True,
                "cached": True,
                "response_time_ms": f"{elapsed*1000:.0f}",
                "message": f"✨ Cached solution with {len(cached_actions)} actions ({elapsed*1000:.0f}ms)"
            }
            metrics.total_success += 1
            metrics.by_type_success[task_type] += 1
            logger.info(f"✅ Task {task_id} cached hit: {len(cached_actions)} actions in {elapsed*1000:.0f}ms")
            return JSONResponse(content=response)
        
        # Step 3: Try specialized template first (very fast, often works)
        logger.info(f"🔧 Generating specialized actions for task type: {task_type}")
        template_actions = TaskClassifier.generate_specialized_actions(task_type, url, prompt)
        
        # Decide: use template only or also try AI?
        # Use template if it's a high-confidence category or if we want speed
        use_template_only = task_type in ["search", "form_fill", "checkout"]
        
        actions = []
        
        if use_template_only:
            # Fast path: use template directly
            logger.info(f"⚡ Using template for high-confidence task type: {task_type}")
            actions = template_actions
        else:
            # Try AI for better accuracy on complex tasks
            logger.info(f"🤖 Attempting AI generation for task type: {task_type}")
            
            ai_prompt = f"""You are a web automation expert. Analyze this {task_type} task and generate optimized browser actions.

Task: {prompt}
URL: {url if url else 'Not specified'}

Generate actions as a JSON array. Each action should have:
- action_type: 'navigate', 'click', 'type', 'wait', 'screenshot', 'scroll', 'select', 'hover', 'key_press'
- Additional fields based on action type

Return ONLY valid JSON array, no markdown or explanation.
Example: [
  {{"action_type": "navigate", "url": "https://example.com"}},
  {{"action_type": "wait", "duration": 2}},
  {{"action_type": "screenshot"}}
]"""
            
            try:
                # Call worker with retry logic
                async def ai_call():
                    gen_request = WorkerRequest(
                        task="generate",
                        input_data={
                            "prompt": ai_prompt,
                            "max_tokens": 2000,
                            "temperature": 0.3
                        }
                    )
                    return await worker.process(gen_request)
                
                gen_response = await RetryHandler.call_with_retry(ai_call, max_retries=2)
                
                if gen_response.success and gen_response.result:
                    try:
                        generated_text = gen_response.result.get("generated_text", "")
                        
                        # Extract JSON from response
                        if "[" in generated_text and "]" in generated_text:
                            json_start = generated_text.index("[")
                            json_end = generated_text.rindex("]") + 1
                            json_str = generated_text[json_start:json_end]
                            ai_actions = json.loads(json_str)
                            logger.info(f"✅ AI generated {len(ai_actions)} actions")
                            actions = ai_actions
                        else:
                            logger.warning(f"⚠️  Could not parse AI response, using template")
                            actions = template_actions
                    except Exception as e:
                        logger.warning(f"⚠️  Error parsing AI actions: {str(e)}, using template")
                        actions = template_actions
                else:
                    logger.warning(f"⚠️  AI generation failed, using template")
                    actions = template_actions
            
            except Exception as e:
                logger.warning(f"⚠️  AI call failed: {str(e)}, using template")
                actions = template_actions
        
        # Step 4: Cache the successful actions
        cache.set(prompt, url, actions)
        
        elapsed = time.time() - start_time
        response = {
            "task_id": task_id,
            "task_type": task_type,
            "actions": actions,
            "success": True,
            "cached": False,
            "response_time_ms": f"{elapsed*1000:.0f}",
            "message": f"✅ Task processed successfully with {len(actions)} actions ({elapsed*1000:.0f}ms)"
        }
        
        metrics.total_success += 1
        metrics.by_type_success[task_type] += 1
        logger.info(f"✅ Task {task_id} completed: {len(actions)} actions in {elapsed*1000:.0f}ms [type: {task_type}]")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"❌ Error solving task: {str(e)}")
        task_id = request_data.get("id", "unknown") if isinstance(request_data, dict) else "unknown"
        metrics.total_errors += 1
        elapsed = time.time() - start_time
        return JSONResponse(
            content={
                "task_id": task_id,
                "success": False,
                "error": str(e),
                "actions": [],
                "response_time_ms": f"{elapsed*1000:.0f}"
            },
            status_code=500
        )


@app.get("/metrics")
async def get_metrics():
    """Get worker metrics for monitoring with task type breakdown"""
    import os
    
    # Get worker uptime
    try:
        start_time = float(os.getenv("WORKER_START_TIME", time.time()))
        uptime_seconds = int(time.time() - start_time)
        uptime_str = f"{uptime_seconds}s"
    except:
        uptime_str = "unknown"
    
    # Calculate success rate
    total = metrics.total_requests
    success_rate = (metrics.total_success / total * 100) if total > 0 else 0
    
    # Convert defaultdicts to regular dicts for JSON serialization
    by_type_dict = dict(metrics.by_type)
    by_type_success_dict = dict(metrics.by_type_success)
    
    # Calculate success rate per type
    success_rate_by_type = {}
    for task_type, count in by_type_dict.items():
        success_count = by_type_success_dict.get(task_type, 0)
        success_rate_by_type[task_type] = f"{(success_count / count * 100):.1f}%" if count > 0 else "0%"
    
    return {
        "worker": worker.worker_name,
        "version": worker.worker_version,
        "status": "operational",
        "uptime": uptime_str,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chutes_api_configured": worker.config.chutes_api_key is not None,
        "capabilities": worker.get_metadata().get("capabilities", []),
        "cache": {
            "size": len(cache.cache),
            "max_size": cache.max_size,
            "ttl_seconds": cache.ttl
        },
        "requests": {
            "total": metrics.total_requests,
            "success": metrics.total_success,
            "errors": metrics.total_errors,
            "success_rate_percent": f"{success_rate:.1f}%"
        },
        "by_task_type": {
            "request_count": by_type_dict,
            "success_count": by_type_success_dict,
            "success_rate_percent": success_rate_by_type
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

