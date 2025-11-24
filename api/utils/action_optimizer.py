"""Action optimization for better accuracy and success rates"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ActionOptimizer:
    """Optimize actions for better accuracy and success rates"""
    
    def __init__(self):
        self.common_patterns = self._load_common_patterns()
    
    def _load_common_patterns(self) -> Dict[str, Any]:
        """Load common successful action patterns"""
        return {
            "login": [
                {"type": "NavigateAction"},
                {"type": "WaitAction", "time_seconds": 1.0},
                {"type": "ScreenshotAction"},
                {"type": "TypeAction"},  # username
                {"type": "TypeAction"},  # password
                {"type": "ClickAction"},  # submit
            ],
            "search": [
                {"type": "NavigateAction"},
                {"type": "WaitAction", "time_seconds": 1.0},
                {"type": "TypeAction"},  # search query
                {"type": "ClickAction"},  # search button
            ],
            "form": [
                {"type": "NavigateAction"},
                {"type": "WaitAction", "time_seconds": 1.0},
                {"type": "ScreenshotAction"},
                # Then fill form fields
            ],
        }
    
    def optimize_action_sequence(self, actions: List[Dict[str, Any]], task_type: str = None) -> List[Dict[str, Any]]:
        """Optimize action sequence for better accuracy"""
        if not actions:
            return actions
        
        optimized = []
        
        # Remove redundant waits (optimize timing)
        prev_action = None
        for action in actions:
            action_type = action.get("type", "")
            
            # Skip redundant waits
            if action_type == "WaitAction" and prev_action and prev_action.get("type") == "WaitAction":
                # Merge consecutive waits
                prev_wait = prev_action.get("time_seconds", 0) or prev_action.get("duration", 0)
                curr_wait = action.get("time_seconds", 0) or action.get("duration", 0)
                optimized[-1]["time_seconds"] = prev_wait + curr_wait
                continue
            
            # Ensure proper action ordering
            if action_type == "NavigateAction" and optimized:
                # Navigate should be first - move to front
                optimized.insert(0, action)
                continue
            
            optimized.append(action)
            prev_action = action
        
        # Validate action sequence
        optimized = self._validate_sequence(optimized)
        
        return optimized
    
    def _validate_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and fix action sequence"""
        if not actions:
            return actions
        
        validated = []
        
        # Ensure NavigateAction is first if URL is present
        navigate_idx = None
        for i, action in enumerate(actions):
            if action.get("type") == "NavigateAction":
                navigate_idx = i
                break
        
        if navigate_idx and navigate_idx > 0:
            # Move NavigateAction to front
            navigate_action = actions.pop(navigate_idx)
            actions.insert(0, navigate_action)
        
        # Ensure actions have required fields
        for action in actions:
            action_type = action.get("type", "")
            
            # Add required fields based on action type
            if action_type == "ClickAction" and not action.get("selector"):
                # Skip invalid click actions
                logger.warning("Skipping ClickAction without selector")
                continue
            
            if action_type == "TypeAction" and not action.get("text"):
                # Skip invalid type actions
                logger.warning("Skipping TypeAction without text")
                continue
            
            validated.append(action)
        
        return validated
    
    def enhance_selectors(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance selectors for better accuracy"""
        enhanced = []
        
        for action in actions:
            if "selector" in action and isinstance(action["selector"], dict):
                selector = action["selector"]
                
                # Ensure selector has required fields
                if selector.get("type") == "attributeValueSelector":
                    if not selector.get("attribute"):
                        # Try to infer attribute
                        value = selector.get("value", "")
                        if value.startswith("#"):
                            selector["attribute"] = "id"
                            selector["value"] = value[1:]
                        elif value.startswith("."):
                            selector["attribute"] = "class"
                            selector["value"] = value[1:]
                        else:
                            selector["attribute"] = "name"
                
                # Ensure case_sensitive is set
                if "case_sensitive" not in selector:
                    selector["case_sensitive"] = False
            
            enhanced.append(action)
        
        return enhanced
    
    def add_verification_steps(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add verification steps for better success rates"""
        verified = []
        
        for i, action in enumerate(actions):
            verified.append(action)
            
            action_type = action.get("type", "")
            
            # Add verification after critical actions
            if action_type in ["ClickAction", "TypeAction", "NavigateAction"]:
                # Add short wait and screenshot for verification
                verified.append({
                    "type": "WaitAction",
                    "time_seconds": 0.5
                })
                # Don't add screenshot after every action (too many)
                # Only add after important actions
                if action_type == "NavigateAction" or (action_type == "ClickAction" and i == len(actions) - 1):
                    verified.append({
                        "type": "ScreenshotAction"
                    })
        
        return verified

