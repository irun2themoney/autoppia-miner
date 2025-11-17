"""Validate generated actions for correctness"""
from typing import Dict, Any, List, Tuple, Optional


class ActionValidator:
    """Validate actions before returning them"""
    
    REQUIRED_FIELDS = {
        "NavigateAction": ["url"],
        "ClickAction": ["selector"],
        "TypeAction": ["selector", "text"],
        "WaitAction": ["time_seconds"],
        "ScreenshotAction": [],
        "ScrollAction": [],
    }
    
    def validate_action(self, action: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a single action"""
        action_type = action.get("type", "")
        
        if not action_type:
            return False, "Action missing 'type' field"
        
        # Check if action type is valid
        if action_type not in self.REQUIRED_FIELDS:
            return False, f"Unknown action type: {action_type}"
        
        # Check required fields
        required = self.REQUIRED_FIELDS[action_type]
        for field in required:
            if field not in action or not action[field]:
                return False, f"{action_type} missing required field: {field}"
        
        # Type-specific validation
        if action_type == "NavigateAction":
            url = action.get("url", "")
            if not url.startswith(("http://", "https://")):
                return False, f"Invalid URL format: {url}"
        
        if action_type == "WaitAction":
            time_seconds = action.get("time_seconds", 0)
            if not isinstance(time_seconds, (int, float)) or time_seconds < 0:
                return False, f"Invalid time_seconds: {time_seconds}"
            if time_seconds > 10:
                return False, f"Wait time too long: {time_seconds}s (max 10s)"
        
        if action_type in ["ClickAction", "TypeAction"]:
            selector = action.get("selector", {})
            if not isinstance(selector, dict):
                return False, f"Selector must be a dict, got: {type(selector)}"
            if "type" not in selector:
                return False, "Selector missing 'type' field"
            if "value" not in selector:
                return False, "Selector missing 'value' field"
        
        if action_type == "TypeAction":
            text = action.get("text", "")
            if not text or len(text) == 0:
                return False, "TypeAction missing or empty 'text' field"
        
        return True, None
    
    def validate_actions(self, actions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Validate list of actions, return valid actions and errors"""
        valid_actions = []
        errors = []
        
        for i, action in enumerate(actions):
            is_valid, error = self.validate_action(action)
            if is_valid:
                valid_actions.append(action)
            else:
                errors.append(f"Action {i}: {error}")
        
        return valid_actions, errors
    
    def fix_common_issues(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Fix common issues in actions"""
        action_type = action.get("type", "")
        
        # Ensure case_sensitive is set for selectors
        if "selector" in action and isinstance(action["selector"], dict):
            if "case_sensitive" not in action["selector"]:
                action["selector"]["case_sensitive"] = False
        
        # Normalize action type
        if action_type and not action_type.endswith("Action"):
            type_map = {
                "click": "ClickAction",
                "type": "TypeAction",
                "wait": "WaitAction",
                "navigate": "NavigateAction",
                "screenshot": "ScreenshotAction",
                "scroll": "ScrollAction",
            }
            normalized = action_type.lower().replace("action", "")
            if normalized in type_map:
                action["type"] = type_map[normalized]
        
        # Fix WaitAction duration field
        if action_type == "WaitAction" and "duration" in action and "time_seconds" not in action:
            action["time_seconds"] = action.pop("duration")
        
        # Ensure URL has protocol
        if action_type == "NavigateAction" and "url" in action:
            url = action["url"]
            if url and not url.startswith(("http://", "https://")):
                action["url"] = "https://" + url
        
        return action

