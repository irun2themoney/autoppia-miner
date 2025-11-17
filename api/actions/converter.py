"""Convert actions to IWA BaseAction format"""
from typing import Dict, Any
from .selectors import create_selector


def convert_to_iwa_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to official IWA BaseAction format"""
    # Handle both old format (action_type) and new format (type from LLM)
    action_type = action.get("type") or action.get("action_type", "")
    
    # Normalize action type (remove "Action" suffix if present, handle case)
    if action_type:
        action_type = action_type.replace("Action", "").lower()
    
    # Map to official action types
    type_map = {
        "click": "ClickAction",
        "type": "TypeAction",
        "wait": "WaitAction",
        "navigate": "NavigateAction",
        "screenshot": "ScreenshotAction",
        "scroll": "ScrollAction",
    }
    
    iwa_type = type_map.get(action_type, action.get("type", "ScreenshotAction"))
    # If already in correct format (from LLM), use it directly
    if iwa_type.endswith("Action") and iwa_type in ["ClickAction", "TypeAction", "WaitAction", 
                                                      "NavigateAction", "ScreenshotAction", "ScrollAction"]:
        result: Dict[str, Any] = {"type": iwa_type}
    else:
        result: Dict[str, Any] = {"type": type_map.get(action_type, "ScreenshotAction")}
    
    # Handle selector
    if "selector" in action and action["selector"]:
        if isinstance(action["selector"], dict):
            result["selector"] = action["selector"]
        else:
            # String selector -> convert to IWA format
            result["selector"] = create_selector(
                "attributeValueSelector",
                action["selector"],
                attribute="custom",
                case_sensitive=False
            )
    
    # Action-specific fields
    if iwa_type == "WaitAction":
        # Handle both "duration" and "time_seconds"
        if "time_seconds" in action:
            result["time_seconds"] = action["time_seconds"]
        elif "duration" in action:
            result["time_seconds"] = action["duration"]
    
    elif iwa_type == "TypeAction":
        if "text" in action:
            result["text"] = action["text"]
        # Selector handled below
    
    elif iwa_type == "NavigateAction":
        if "url" in action:
            result["url"] = action["url"]
    
    elif iwa_type == "ScrollAction":
        direction = action.get("direction", "down").lower()
        if direction == "down":
            result["down"] = True
        elif direction == "up":
            result["up"] = True
        elif direction == "left":
            result["left"] = True
        elif direction == "right":
            result["right"] = True
    
    return result

