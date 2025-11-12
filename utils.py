"""
Utility functions for Autoppia Worker
"""

import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file
    
    Args:
        config_path: Path to configuration file. If None, looks for config.yaml
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = "config.yaml"
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, "r") as f:
        if config_path.endswith(".yaml") or config_path.endswith(".yml"):
            return yaml.safe_load(f)
        elif config_path.endswith(".json"):
            return json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path}")


def load_template(template_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load worker template from JSON file
    
    Args:
        template_path: Path to template file. If None, looks for template.json
        
    Returns:
        Template dictionary
    """
    if template_path is None:
        template_path = "template.json"
    
    template_file = Path(template_path)
    
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_file, "r") as f:
        return json.load(f)


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate worker configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ["api_key"]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required configuration field: {field}")
    
    return True

