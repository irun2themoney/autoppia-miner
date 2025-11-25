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
    
    # Map to official action types (from Autoppia framework)
    type_map = {
        "click": "ClickAction",
        "type": "TypeAction",
        "wait": "WaitAction",
        "navigate": "NavigateAction",
        "goto": "NavigateAction",  # goto maps to NavigateAction
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
    
    # Handle selector - ensure proper IWA Selector format
    if "selector" in action and action["selector"]:
        if isinstance(action["selector"], dict):
            selector = action["selector"]
            # Ensure selector has required fields for IWA format
            if "type" not in selector:
                # Convert old format to new IWA format
                # CRITICAL FIX: Convert case_sensitive to caseSensitive (camelCase)
                case_sensitive_val = selector.get("case_sensitive", selector.get("caseSensitive", False))
                if "attributeValueSelector" in selector:
                    result["selector"] = {
                        "type": "attributeValueSelector",
                        "attribute": selector.get("attribute", "id"),
                        "value": selector.get("value", selector.get("attributeValueSelector", "")),
                        "caseSensitive": case_sensitive_val  # camelCase for validator
                    }
                elif "tagContainsSelector" in selector:
                    result["selector"] = {
                        "type": "tagContainsSelector",
                        "value": selector.get("value", selector.get("tagContainsSelector", "")),
                        "caseSensitive": case_sensitive_val  # camelCase for validator
                    }
                else:
                    # Fallback: assume attribute selector
                    result["selector"] = {
                        "type": "attributeValueSelector",
                        "attribute": "id",
                        "value": str(selector),
                        "caseSensitive": False  # camelCase for validator
                    }
            else:
                # Already in correct format - but ensure only camelCase (remove snake_case if present)
                cleaned_selector = dict(selector)
                # CRITICAL FIX: Remove snake_case if camelCase exists (avoid duplicate fields)
                if "caseSensitive" in cleaned_selector and "case_sensitive" in cleaned_selector:
                    del cleaned_selector["case_sensitive"]
                result["selector"] = cleaned_selector
        else:
            # String selector -> convert to IWA format
            selector_str = str(action["selector"])
            # CRITICAL FIX: Use camelCase (caseSensitive) not snake_case (case_sensitive)
            if selector_str.startswith("#"):
                # ID selector
                result["selector"] = {
                    "type": "attributeValueSelector",
                    "attribute": "id",
                    "value": selector_str[1:],  # Remove #
                    "caseSensitive": False  # camelCase for validator
                }
            elif selector_str.startswith("."):
                # Class selector
                result["selector"] = {
                    "type": "attributeValueSelector",
                    "attribute": "class",
                    "value": selector_str[1:],  # Remove .
                    "caseSensitive": False  # camelCase for validator
                }
            else:
                # Text selector
                result["selector"] = {
                    "type": "tagContainsSelector",
                    "value": selector_str,
                    "caseSensitive": False  # camelCase for validator
                }
    
    # Action-specific fields
    # CRITICAL FIX: Validator expects camelCase (timeSeconds) not snake_case (time_seconds)
    if iwa_type == "WaitAction":
        # Handle both "duration" and "time_seconds" (convert to camelCase)
        if "timeSeconds" in action:
            result["timeSeconds"] = action["timeSeconds"]
        elif "time_seconds" in action:
            result["timeSeconds"] = action["time_seconds"]  # Convert to camelCase
        elif "duration" in action:
            result["timeSeconds"] = action["duration"]  # Convert to camelCase
    
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

