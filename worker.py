"""
Autoppia AI Worker - Main Worker Implementation
This worker follows the Autoppia SDK patterns for framework-agnostic AI workers.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from loguru import logger
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()


class WorkerConfig(BaseModel):
    """Worker configuration model"""
    api_key: str = Field(default="", description="API key for authentication")
    chutes_api_key: Optional[str] = Field(default=None, description="Chutes API key")
    model: str = Field(default="gpt-4", description="AI model to use")
    max_tokens: int = Field(default=1000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.7, description="Temperature for AI generation")
    chutes_api_url: str = Field(default="https://api.chutes.ai", description="Chutes API base URL")
    
    model_config = {"extra": "allow"}  # Allow additional configuration fields


class WorkerRequest(BaseModel):
    """Request model for worker inputs"""
    task: str = Field(..., description="Task to perform")
    input_data: Optional[Dict[str, Any]] = Field(default=None, description="Input data for the task")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Additional parameters")


class WorkerResponse(BaseModel):
    """Response model for worker outputs"""
    success: bool = Field(..., description="Whether the task was successful")
    result: Optional[Any] = Field(default=None, description="Task result")
    error: Optional[str] = Field(default=None, description="Error message if any")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class AutoppiaWorker:
    """
    Autoppia AI Worker Class
    This is the main worker class that implements the Autoppia worker interface.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Autoppia Worker
        
        Args:
            config: Optional configuration dictionary. If not provided, loads from environment.
        """
        self.config = self._load_config(config)
        self.worker_name = os.getenv("WORKER_NAME", "autoppia-miner")
        self.worker_version = os.getenv("WORKER_VERSION", "0.1.0")
        
        # Initialize logger
        logger.add(
            f"logs/{self.worker_name}.log",
            rotation="10 MB",
            retention="7 days",
            level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # Initialize HTTP client for Chutes API
        self.chutes_client = None
        if self.config.chutes_api_key:
            self.chutes_client = httpx.AsyncClient(
                base_url=self.config.chutes_api_url,
                headers={
                    "Authorization": f"Bearer {self.config.chutes_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            logger.info("Chutes API client initialized")
        
        logger.info(f"Initializing {self.worker_name} v{self.worker_version}")
        logger.info(f"Worker configuration loaded: model={self.config.model}")
    
    def _load_config(self, config: Optional[Dict[str, Any]] = None) -> WorkerConfig:
        """Load configuration from dict or environment variables"""
        if config:
            return WorkerConfig(**config)
        
        # Load from environment
        return WorkerConfig(
            api_key=os.getenv("AUTOPPIA_API_KEY", ""),
            chutes_api_key=os.getenv("CHUTES_API_KEY"),
            model=os.getenv("MODEL", "gpt-4"),
            max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
            chutes_api_url=os.getenv("CHUTES_API_URL", "https://api.chutes.ai")
        )
    
    async def process(self, request: WorkerRequest) -> WorkerResponse:
        """
        Main processing method - implements the Autoppia worker interface
        
        Args:
            request: WorkerRequest containing task and input data
            
        Returns:
            WorkerResponse with results or error
        """
        try:
            logger.info(f"Processing task: {request.task}")
            
            # Route to appropriate handler based on task type
            if request.task == "mine":
                result = await self._handle_mine(request)
            elif request.task == "process":
                result = await self._handle_process(request)
            elif request.task == "generate":
                result = await self._handle_generate(request)
            else:
                return WorkerResponse(
                    success=False,
                    error=f"Unknown task type: {request.task}",
                    metadata={"supported_tasks": ["mine", "process", "generate"]}
                )
            
            return WorkerResponse(
                success=True,
                result=result,
                metadata={
                    "task": request.task,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "worker": self.worker_name,
                    "version": self.worker_version
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return WorkerResponse(
                success=False,
                error=str(e),
                metadata={
                    "task": request.task,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def _handle_mine(self, request: WorkerRequest) -> Dict[str, Any]:
        """Handle mining tasks"""
        logger.info("Executing mine task")
        
        # Extract mining parameters
        input_data = request.input_data or {}
        source = input_data.get("source", "")
        pattern = input_data.get("pattern", "")
        
        # Implement mining logic here
        # This is a placeholder - implement your specific mining logic
        result = {
            "mined_data": [],
            "source": source,
            "pattern": pattern,
            "count": 0
        }
        
        logger.info(f"Mining completed: {result['count']} items found")
        return result
    
    async def _handle_process(self, request: WorkerRequest) -> Dict[str, Any]:
        """Handle data processing tasks"""
        logger.info("Executing process task")
        
        input_data = request.input_data or {}
        data = input_data.get("data", [])
        
        # Implement processing logic here
        processed_data = []
        for item in data:
            # Process each item
            processed_item = {
                "original": item,
                "processed": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            processed_data.append(processed_item)
        
        result = {
            "processed_count": len(processed_data),
            "data": processed_data
        }
        
        logger.info(f"Processing completed: {result['processed_count']} items")
        return result
    
    async def _handle_generate(self, request: WorkerRequest) -> Dict[str, Any]:
        """Handle AI generation tasks using Chutes API"""
        logger.info("Executing generate task")
        
        input_data = request.input_data or {}
        prompt = input_data.get("prompt", "")
        model = input_data.get("model") or self.config.model
        max_tokens = input_data.get("max_tokens") or self.config.max_tokens
        temperature = input_data.get("temperature") or self.config.temperature
        
        # Use Chutes API if available
        if self.chutes_client and self.config.chutes_api_key:
            try:
                logger.info(f"Using Chutes API for generation with model: {model}")
                
                # Try chat completions endpoint first
                chat_messages = input_data.get("messages", [{"role": "user", "content": prompt}])
                
                # Prepare request payload
                payload = {
                    "model": model,
                    "messages": chat_messages if isinstance(chat_messages, list) else [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                # Add any additional parameters
                if request.parameters:
                    payload.update(request.parameters)
                
                # Try different Chutes API endpoints
                # First, try the standard chat completions endpoint
                endpoints_to_try = [
                    "/v1/chat/completions",
                    "/chat/completions",
                    "/api/v1/chat/completions"
                ]
                
                response = None
                last_error = None
                
                for endpoint in endpoints_to_try:
                    try:
                        logger.info(f"Trying Chutes API endpoint: {endpoint}")
                        response = await self.chutes_client.post(
                            endpoint,
                            json=payload
                        )
                        if response.status_code == 200:
                            break
                        else:
                            logger.warning(f"Endpoint {endpoint} returned {response.status_code}")
                    except httpx.HTTPStatusError as e:
                        last_error = e
                        logger.warning(f"Endpoint {endpoint} failed: {e.response.status_code}")
                        continue
                    except Exception as e:
                        last_error = e
                        logger.warning(f"Endpoint {endpoint} error: {str(e)}")
                        continue
                
                if response is None or response.status_code != 200:
                    if last_error:
                        raise last_error
                    else:
                        raise Exception(f"All endpoints failed. Last status: {response.status_code if response else 'None'}")
                
                response.raise_for_status()
                
                api_response = response.json()
                
                # Extract generated text
                generated_text = ""
                tokens_used = 0
                
                if "choices" in api_response and len(api_response["choices"]) > 0:
                    generated_text = api_response["choices"][0].get("message", {}).get("content", "")
                
                if "usage" in api_response:
                    tokens_used = api_response["usage"].get("total_tokens", 0)
                
                result = {
                    "generated_text": generated_text,
                    "model": model,
                    "tokens_used": tokens_used,
                    "provider": "chutes",
                    "raw_response": api_response
                }
                
                logger.info(f"Generation completed via Chutes API. Tokens used: {tokens_used}")
                return result
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Chutes API HTTP error: {e.response.status_code} - {e.response.text}")
                # Fall back to placeholder
            except Exception as e:
                logger.error(f"Chutes API error: {str(e)}")
                # Fall back to placeholder
        
        # Fallback placeholder implementation
        logger.warning("Chutes API not configured or failed, using placeholder")
        result = {
            "generated_text": f"Generated response for: {prompt}",
            "model": model,
            "tokens_used": 0,
            "provider": "placeholder",
            "note": "Chutes API not configured. Set CHUTES_API_KEY in environment variables."
        }
        
        logger.info("Generation completed (placeholder)")
        return result
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get worker metadata for Autoppia marketplace"""
        return {
            "name": self.worker_name,
            "version": self.worker_version,
            "description": os.getenv("WORKER_DESCRIPTION", "An Autoppia AI Worker"),
            "capabilities": ["text_processing", "data_mining", "ai_generation"],
            "framework": "framework-agnostic",
            "privacy_preserving": True
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint for Autoppia infrastructure"""
        health_status = {
            "status": "healthy",
            "worker": self.worker_name,
            "version": self.worker_version,
            "timestamp": datetime.utcnow().isoformat(),
            "chutes_api_configured": self.config.chutes_api_key is not None
        }
        
        # Test Chutes API connection if configured
        if self.chutes_client and self.config.chutes_api_key:
            try:
                # Simple health check - try to ping the API
                response = await self.chutes_client.get("/health", timeout=5.0)
                health_status["chutes_api_status"] = "connected" if response.status_code == 200 else "error"
            except Exception as e:
                health_status["chutes_api_status"] = f"error: {str(e)}"
        
        return health_status
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources"""
        if self.chutes_client:
            await self.chutes_client.aclose()


# Main entry point for Autoppia SDK
async def main():
    """Main entry point - integrates with Autoppia SDK"""
    # Initialize worker
    worker = AutoppiaWorker()
    
    # Example usage
    logger.info("Worker initialized successfully")
    logger.info(f"Worker metadata: {json.dumps(worker.get_metadata(), indent=2)}")
    
    # Health check
    health = await worker.health_check()
    logger.info(f"Health check: {json.dumps(health, indent=2)}")
    
    # Example request processing
    example_request = WorkerRequest(
        task="mine",
        input_data={
            "source": "example_source",
            "pattern": "example_pattern"
        }
    )
    
    response = await worker.process(example_request)
    logger.info(f"Example response: {json.dumps(response.dict(), indent=2)}")


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the worker
    asyncio.run(main())

