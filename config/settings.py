"""Settings management using pydantic"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    
    # Agent Configuration
    agent_type: str = "hybrid"  # template, chutes, hybrid, or browser-use
    llm_provider: Optional[str] = None  # openai, chutes, or None
    
    # Chutes API Configuration
    chutes_api_key: Optional[str] = None
    chutes_api_url: str = "https://api.chutes.ai/v1/chat/completions"
    chutes_model: str = "Qwen/Qwen2.5-7B-Instruct"  # Free model! Options: Qwen/Qwen2.5-7B-Instruct, Qwen/Qwen3-32B, gpt-4o-mini, etc.
    
    # Miner Configuration
    subnet_uid: int = 36
    network: str = "finney"
    axon_port: int = 8091
    api_url: str = "http://localhost:8080"
    api_timeout: float = 30.0
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix, use exact variable names
        extra = "ignore"  # Ignore extra fields from .env (for backward compatibility)


# Global settings instance
settings = Settings()

