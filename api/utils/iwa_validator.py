"""IWA Format Validator - Ensures actions comply with Autoppia IWA format"""
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Valid IWA action types
VALID_ACTION_TYPES = {
    "ClickAction",
    "TypeAction",
    "WaitAction",
    "NavigateAction",
    "ScreenshotAction",
    "ScrollAction"
}

# Valid selector types
VALID_SELECTOR_TYPES = {
    "tagContainsSelector",
    "attributeValueSelector",
    "cssSelector",
    "xpathSelector"
}


def validate_iwa_action(action: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a single IWA action format
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(action, dict):
        return False, "Action must be a dictionary"
    
    # Check required 'type' field
    if "type" not in action:
        return False, "Action missing required 'type' field"
    
    action_type = action["type"]
    if action_type not in VALID_ACTION_TYPES:
        return False, f"Invalid action type '{action_type}'. Must be one of {VALID_ACTION_TYPES}"
    
    # Validate action-specific fields
    # CRITICAL FIX: Validator expects camelCase (timeSeconds) not snake_case (time_seconds)
    if action_type == "WaitAction":
        # Check for camelCase first (validator expects this)
        if "timeSeconds" not in action:
            # Fallback: also check snake_case for backward compatibility
            if "time_seconds" not in action:
                return False, "WaitAction missing required 'timeSeconds' field"
            # Convert snake_case to camelCase for validation
            action["timeSeconds"] = action["time_seconds"]
        if not isinstance(action.get("timeSeconds", action.get("time_seconds")), (int, float)):
            return False, "WaitAction 'timeSeconds' must be a number"
    
    elif action_type == "TypeAction":
        if "text" not in action:
            return False, "TypeAction missing required 'text' field"
        if "selector" not in action:
            return False, "TypeAction missing required 'selector' field"
        selector_valid, selector_error = validate_selector(action["selector"])
        if not selector_valid:
            return False, f"TypeAction selector invalid: {selector_error}"
    
    elif action_type == "ClickAction":
        if "selector" not in action:
            return False, "ClickAction missing required 'selector' field"
        selector_valid, selector_error = validate_selector(action["selector"])
        if not selector_valid:
            return False, f"ClickAction selector invalid: {selector_error}"
    
    elif action_type == "NavigateAction":
        if "url" not in action:
            return False, "NavigateAction missing required 'url' field"
        if not isinstance(action["url"], str):
            return False, "NavigateAction 'url' must be a string"
    
    elif action_type == "ScrollAction":
        # Must have at least one direction
        directions = ["down", "up", "left", "right"]
        has_direction = any(action.get(d) for d in directions)
        if not has_direction:
            return False, "ScrollAction must have at least one direction (down, up, left, right)"
    
    # ScreenshotAction has no required fields
    
    return True, ""


def validate_selector(selector: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate IWA selector format
    
    CRITICAL FIX: Validator expects camelCase (caseSensitive) not snake_case (case_sensitive)
    
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(selector, dict):
        return False, "Selector must be a dictionary"
    
    if "type" not in selector:
        return False, "Selector missing required 'type' field"
    
    selector_type = selector["type"]
    if selector_type not in VALID_SELECTOR_TYPES:
        return False, f"Invalid selector type '{selector_type}'. Must be one of {VALID_SELECTOR_TYPES}"
    
    # CRITICAL FIX: Convert snake_case to camelCase if present (for backward compatibility)
    if "case_sensitive" in selector and "caseSensitive" not in selector:
        selector["caseSensitive"] = selector["case_sensitive"]
    
    # Validate selector-specific fields
    if selector_type == "tagContainsSelector":
        if "value" not in selector:
            return False, "tagContainsSelector missing required 'value' field"
    
    elif selector_type == "attributeValueSelector":
        if "attribute" not in selector:
            return False, "attributeValueSelector missing required 'attribute' field"
        if "value" not in selector:
            return False, "attributeValueSelector missing required 'value' field"
    
    elif selector_type == "cssSelector":
        if "value" not in selector:
            return False, "cssSelector missing required 'value' field"
    
    elif selector_type == "xpathSelector":
        if "value" not in selector:
            return False, "xpathSelector missing required 'value' field"
    
    return True, ""


def validate_iwa_action_sequence(actions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Validate a sequence of IWA actions
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(actions, list):
        return False, ["Actions must be a list"]
    
    if len(actions) == 0:
        return False, ["Actions list cannot be empty"]
    
    for i, action in enumerate(actions):
        is_valid, error = validate_iwa_action(action)
        if not is_valid:
            errors.append(f"Action {i}: {error}")
    
    return len(errors) == 0, errors


def log_action_validation(actions: List[Dict[str, Any]], context: str = "") -> bool:
    """
    Validate and log IWA action sequence
    
    Returns:
        True if valid, False otherwise
    """
    is_valid, errors = validate_iwa_action_sequence(actions)
    
    if is_valid:
        logger.info(f"✅ IWA Validation PASSED: {len(actions)} actions valid {context}")
        return True
    else:
        logger.error(f"❌ IWA Validation FAILED {context}:")
        for error in errors:
            logger.error(f"   - {error}")
        return False

