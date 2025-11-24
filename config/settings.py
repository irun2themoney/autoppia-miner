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
    agent_type: str = "template"  # SIMPLIFIED: Use simple template agent
    
    # Miner Configuration
    subnet_uid: int = 36
    network: str = "finney"
    axon_port: int = 8091
    api_url: str = "http://localhost:8080"
    api_timeout: float = 90.0  # Updated to match validators (Nov 2025: increased from 30s to 90s)
    
    # Wallet Configuration
    wallet_name: Optional[str] = None
    wallet_hotkey: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Self-Learning Configuration
    self_learning_enabled: bool = True  # Enable self-learning from official docs
    self_learning_interval: int = 3600  # Check for updates every hour (seconds)
    
    # Browser Automation Configuration
    enable_browser_automation: bool = True  # Enable Playwright browser automation (better accuracy, slower)
    browser_automation_timeout: float = 15.0  # Timeout for browser page loads (seconds)
    
    # Performance Optimization Settings
    fast_mode: bool = True  # Enable fast mode: optimize for speed while maintaining accuracy
    browser_fetch_timeout: float = 3.0  # Reduced from 5.0s - faster browser fetching
    dom_analysis_timeout: float = 1.5  # Reduced from 2.0s - faster DOM analysis
    enable_selector_caching: bool = True  # Cache common selectors for faster responses
    parallel_processing: bool = True  # Enable parallel processing where possible
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix, use exact variable names
        extra = "ignore"  # Ignore extra fields from .env (for backward compatibility)


# Global settings instance
settings = Settings()

