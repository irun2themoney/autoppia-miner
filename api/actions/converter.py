"""Convert actions to IWA BaseAction format"""
from typing import Dict, Any
from .selectors import create_selector


def convert_to_iwa_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to official IWA BaseAction format"""
    action_type = action.get("action_type", "")
    
    # Map to official action types
    type_map = {
        "click": "ClickAction",
        "type": "TypeAction",
        "wait": "WaitAction",
        "navigate": "NavigateAction",
        "screenshot": "ScreenshotAction",
        "scroll": "ScrollAction",
    }
    
    iwa_type = type_map.get(action_type, "ScreenshotAction")
    result: Dict[str, Any] = {"type": iwa_type}
    
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
        if "duration" in action:
            result["time_seconds"] = action["duration"]
    
    elif iwa_type == "TypeAction":
        if "text" in action:
            result["text"] = action["text"]
        if "selector" in action:
            result["selector"] = action["selector"]
    
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

