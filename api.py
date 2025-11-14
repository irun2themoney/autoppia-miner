"""
IWA API Server - Official Pattern
Based on ApifiedWebAgent from autoppia_iwa
"""

import re
from typing import Dict, Any, List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="IWA Miner", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


def create_selector(selector_type: str, value: str, attribute: str = None, case_sensitive: bool = False) -> Dict[str, Any]:
    """Create IWA selector object"""
    selector = {
        "type": selector_type,
        "value": value,
        "case_sensitive": case_sensitive
    }
    if attribute:
        selector["attribute"] = attribute
    return selector


def extract_keywords(prompt: str) -> Dict[str, List[str]]:
    """Extract keywords from prompt for smart action generation"""
    prompt_lower = prompt.lower()
    
    # Action keywords
    action_keywords = []
    if any(w in prompt_lower for w in ["click", "select", "choose", "pick"]):
        action_keywords.append("click")
    if any(w in prompt_lower for w in ["type", "enter", "fill", "input"]):
        action_keywords.append("type")
    if any(w in prompt_lower for w in ["search", "find", "look"]):
        action_keywords.append("search")
    if any(w in prompt_lower for w in ["switch", "toggle", "change", "view"]):
        action_keywords.append("switch")
    
    # Target keywords (what to interact with)
    target_keywords = []
    for word in ["month", "week", "day", "year", "button", "link", "submit", "login"]:
        if word in prompt_lower:
            target_keywords.append(word)
    
    return {"actions": action_keywords, "targets": target_keywords}


def generate_selector_strategies(prompt: str) -> List[Dict[str, Any]]:
    """
    Generate multiple selector strategies with fallbacks.
    Returns list of selectors to try in order - if first fails, try next.
    IWA uses dynamic environments (D1-D4), so we need multiple strategies.
    """
    prompt_lower = prompt.lower()
    strategies = []
    
    # Calendar view selectors - multiple strategies
    if "month" in prompt_lower or "month view" in prompt_lower:
        # Strategy 1: Exact text "Month" (most common)
        strategies.append(create_selector("tagContainsSelector", "Month", case_sensitive=False))
        # Strategy 2: Try "Monthly" (alternative text)
        strategies.append(create_selector("tagContainsSelector", "Monthly", case_sensitive=False))
        # Strategy 3: Try "Month View" (full phrase)
        strategies.append(create_selector("tagContainsSelector", "Month View", case_sensitive=False))
        # Strategy 4: Try attribute selectors (data-testid, aria-label)
        strategies.append(create_selector("attributeValueSelector", "month", attribute="data-testid", case_sensitive=False))
        strategies.append(create_selector("attributeValueSelector", "month", attribute="aria-label", case_sensitive=False))
        # Strategy 5: Generic button fallback
        strategies.append(create_selector("attributeValueSelector", "button", attribute="custom", case_sensitive=False))
        return strategies
    
    if "week" in prompt_lower or "week view" in prompt_lower:
        # Strategy 1: Exact text "Week"
        strategies.append(create_selector("tagContainsSelector", "Week", case_sensitive=False))
        # Strategy 2: Try "Weekly"
        strategies.append(create_selector("tagContainsSelector", "Weekly", case_sensitive=False))
        # Strategy 3: Try "Week View"
        strategies.append(create_selector("tagContainsSelector", "Week View", case_sensitive=False))
        # Strategy 4: Attribute selectors
        strategies.append(create_selector("attributeValueSelector", "week", attribute="data-testid", case_sensitive=False))
        strategies.append(create_selector("attributeValueSelector", "week", attribute="aria-label", case_sensitive=False))
        # Strategy 5: Generic fallback
        strategies.append(create_selector("attributeValueSelector", "button", attribute="custom", case_sensitive=False))
        return strategies
    
    if "day" in prompt_lower or "day view" in prompt_lower:
        strategies.append(create_selector("tagContainsSelector", "Day", case_sensitive=False))
        strategies.append(create_selector("tagContainsSelector", "Daily", case_sensitive=False))
        strategies.append(create_selector("tagContainsSelector", "Day View", case_sensitive=False))
        strategies.append(create_selector("attributeValueSelector", "day", attribute="data-testid", case_sensitive=False))
        strategies.append(create_selector("attributeValueSelector", "button", attribute="custom", case_sensitive=False))
        return strategies
    
    # Generic click targets
    keywords = extract_keywords(prompt)
    
    # Priority words
    priority_words = ["month", "week", "day", "year", "view"]
    for word in priority_words:
        if word in prompt_lower:
            strategies.append(create_selector("tagContainsSelector", word.title(), case_sensitive=False))
            break
    
    # Try target keywords
    if keywords["targets"]:
        target = keywords["targets"][0].title()
        strategies.append(create_selector("tagContainsSelector", target, case_sensitive=False))
    
    # Try action keywords
    if keywords["actions"]:
        action = keywords["actions"][0].title()
        strategies.append(create_selector("tagContainsSelector", action, case_sensitive=False))
    
    # Fallback: generic button selector
    if not strategies:
        strategies.append(create_selector("attributeValueSelector", "button:first-of-type", attribute="custom", case_sensitive=False))
    
    return strategies


def generate_smart_selector(prompt: str) -> Dict[str, Any]:
    """
    Generate smart selector with multiple strategies for robustness.
    IWA uses dynamic environments (D1-D4), so we need flexible selectors.
    """
    prompt_lower = prompt.lower()
    
    # Calendar view selectors - try multiple strategies
    if "month" in prompt_lower or "month view" in prompt_lower:
        # Strategy 1: Text matching (most common)
        # tagContainsSelector matches text content, case-insensitive
        # This will match "Month", "month", "Monthly", "Month View", etc.
        return create_selector("tagContainsSelector", "Month", case_sensitive=False)
    
    if "week" in prompt_lower or "week view" in prompt_lower:
        # Strategy 1: Text matching
        return create_selector("tagContainsSelector", "Week", case_sensitive=False)
    
    if "day" in prompt_lower or "day view" in prompt_lower:
        return create_selector("tagContainsSelector", "Day", case_sensitive=False)
    
    # Generic click targets - try text first, then attributes
    keywords = extract_keywords(prompt)
    
    # Priority: specific target words (month, week, etc.)
    priority_words = ["month", "week", "day", "year", "view"]
    for word in priority_words:
        if word in prompt_lower:
            return create_selector("tagContainsSelector", word.title(), case_sensitive=False)
    
    # Try target keywords
    if keywords["targets"]:
        target = keywords["targets"][0].title()
        return create_selector("tagContainsSelector", target, case_sensitive=False)
    
    # Try action keywords
    if keywords["actions"]:
        action = keywords["actions"][0].title()
        return create_selector("tagContainsSelector", action, case_sensitive=False)
    
    # Fallback: generic button selector
    return create_selector("attributeValueSelector", "button:first-of-type", attribute="custom", case_sensitive=False)


def generate_actions(prompt: str, url: str) -> List[Dict[str, Any]]:
    """Generate action sequence based on prompt"""
    actions = []
    prompt_lower = prompt.lower()
    
    # Navigate if URL provided
    if url:
        actions.append({"action_type": "navigate", "url": url})
        actions.append({"action_type": "wait", "duration": 1.2})  # Longer wait for page load
    
    # Initial screenshot
    actions.append({"action_type": "screenshot"})
    
    # Determine task type and generate actions
    if any(w in prompt_lower for w in ["click", "select", "choose", "switch", "toggle", "view"]):
        # Click task - wait for elements to be ready
        # For calendar views, elements might need more time to render
        actions.append({"action_type": "wait", "duration": 1.0})  # Wait for dynamic content to stabilize
        
        # Generate multiple selector strategies for robustness
        selector_strategies = generate_selector_strategies(prompt)
        
        # Try primary selector first
        actions.append({
            "action_type": "click",
            "selector": selector_strategies[0]
        })
        actions.append({"action_type": "wait", "duration": 0.3})  # Short wait to check if click worked
        
        # Add fallback selectors (try 2-3 most likely alternatives)
        # If first selector fails, these will be tried
        for selector in selector_strategies[1:3]:  # Try up to 2 fallbacks
            actions.append({
                "action_type": "click",
                "selector": selector
            })
            actions.append({"action_type": "wait", "duration": 0.3})
        
        actions.append({"action_type": "wait", "duration": 2.5})  # Final wait for view change
        actions.append({"action_type": "screenshot"})
    
    elif any(w in prompt_lower for w in ["type", "enter", "fill", "input"]):
        # Type task
        # Find input field
        if "email" in prompt_lower:
            selector = create_selector("attributeValueSelector", "email", attribute="type")
            text = "test@example.com"
        elif "password" in prompt_lower:
            selector = create_selector("attributeValueSelector", "password", attribute="type")
            text = "password123"
        else:
            selector = create_selector("attributeValueSelector", "input:first-of-type", attribute="custom")
            text = "test"
        
        actions.append({
            "action_type": "click",
            "selector": selector
        })
        actions.append({"action_type": "wait", "duration": 0.2})
        actions.append({
            "action_type": "type",
            "text": text,
            "selector": selector
        })
        actions.append({"action_type": "wait", "duration": 0.5})
        actions.append({"action_type": "screenshot"})
    
    elif any(w in prompt_lower for w in ["search", "find", "look"]):
        # Search task
        search_query = "test query"
        # Extract query from prompt if possible
        words = prompt.split()
        for i, word in enumerate(words):
            if word.lower() in ["for", "search", "find"] and i + 1 < len(words):
                search_query = words[i + 1]
                break
        
        selector = create_selector("attributeValueSelector", "search", attribute="type")
        actions.append({
            "action_type": "click",
            "selector": selector
        })
        actions.append({"action_type": "wait", "duration": 0.2})
        actions.append({
            "action_type": "type",
            "text": search_query,
            "selector": selector
        })
        actions.append({"action_type": "wait", "duration": 1.0})
        actions.append({"action_type": "screenshot"})
    
    else:
        # Generic: just screenshot
        actions.append({"action_type": "wait", "duration": 0.5})
        actions.append({"action_type": "screenshot"})
    
    return actions


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
    
    return result


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.options("/solve_task")
async def solve_task_options():
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        }
    )


@app.post("/solve_task")
async def solve_task(request_data: Dict[str, Any]):
    """
    Main endpoint - matches ApifiedWebAgent expectations
    Input: task.clean_task() format
    Output: {actions: [], web_agent_id: str, recording: str}
    """
    try:
        task_id = request_data.get("id", "unknown")
        prompt = request_data.get("prompt", "")
        url = request_data.get("url", "")
        
        # Generate actions
        raw_actions = generate_actions(prompt, url)
        
        # Convert to IWA format
        iwa_actions = [convert_to_iwa_action(action) for action in raw_actions]
        
        # Ensure non-empty (critical for playground)
        if not iwa_actions:
            iwa_actions = [{"type": "ScreenshotAction"}]
        
        return JSONResponse(
            content={
                "actions": iwa_actions,
                "web_agent_id": task_id,
                "recording": "",
                # Additional fields for compatibility
                "id": task_id,
                "task_id": task_id,
            },
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    except Exception as e:
        # Return empty actions on error (playground expects this)
        return JSONResponse(
            content={
                "actions": [],
                "web_agent_id": request_data.get("id", "unknown"),
                "recording": "",
            },
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
