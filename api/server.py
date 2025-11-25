"""FastAPI server setup"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .endpoints import router
# SIMPLIFIED: Removed feedback endpoints (not needed for core functionality)
# SIMPLIFIED: Removed dashboard and learning endpoints (not needed)
from config.settings import settings
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# CORS headers helper (used in multiple places)
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
}

# SIMPLIFIED: Removed self-learning system (not needed for simple miner)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    EXPERT LLM FEEDBACK: Initialize browser at startup to avoid 2-4s delay per request
    """
    # EXPERT LLM FEEDBACK: Start browser instance at startup (critical for < 1.5s response time)
    # Starting a new browser for every request takes 2-4 seconds alone, guaranteeing timeout
    logger.info("🚀 Starting API server...")
    
    try:
        from api.utils.browser_analyzer import _get_browser, close_browser
        # Pre-initialize browser instance (singleton pattern)
        browser = await _get_browser()
        if browser:
            logger.info("✅ Playwright browser instance cached at startup (critical for performance)")
        else:
            logger.warning("⚠️ Failed to initialize browser at startup - will be lazy-loaded")
    except Exception as e:
        logger.warning(f"⚠️ Browser initialization at startup failed (non-critical): {e}")
        logger.info("   Browser will be initialized on first use (slower)")
    
    yield
    
    # Cleanup: Close browser on shutdown
    try:
        from api.utils.browser_analyzer import close_browser
        await close_browser()
        logger.info("✅ Browser instance closed on shutdown")
    except Exception as e:
        logger.warning(f"⚠️ Error closing browser on shutdown: {e}")


app = FastAPI(
    title="IWA Miner API",
    version="1.0.0",
    description="Infinite Web Arena Miner API - ApifiedWebAgent Pattern",
    lifespan=lifespan
)

# CRITICAL: Handle validation errors to ensure we never return empty actions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors - always return actions (benchmark requirement)"""
    logger.warning(f"Validation error for {request.url}: {exc.errors()}")
    # Extract request body if possible
    try:
        body = await request.json()
        task_id = body.get("id", "unknown")
    except:
        task_id = "unknown"
    
    # CRITICAL: Always return actions, even on validation error
    # Match official format: {actions: [], web_agent_id: str, recording: str}
    return JSONResponse(
        content={
            "actions": [{"type": "ScreenshotAction"}],  # At least one action
            "web_agent_id": task_id,
            "recording": "",
        },
        status_code=200,  # Return 200 with fallback actions
        headers=CORS_HEADERS
    )

# SIMPLIFIED: Removed static files (dashboard not needed)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
# SIMPLIFIED: Removed feedback, dashboard and learning routers (not needed)


@app.get("/health")
async def health():
    """Health check endpoint - SIMPLIFIED"""
    agent_type = os.getenv("AGENT_TYPE", settings.agent_type)
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agent_type": agent_type,
    }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint - SIMPLIFIED: Returns empty metrics"""
    return JSONResponse(
        content={"status": "ok", "metrics": {}},
        headers=CORS_HEADERS
    )


@app.get("/")
async def root():
    """Root endpoint for testing"""
    return JSONResponse(
        content={
            "status": "online",
            "version": "1.0.0",
                "endpoints": {
                    "solve_task": "/solve_task",
                    "health": "/health",
                    "metrics": "/metrics"
                }
        },
        headers=CORS_HEADERS
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )

