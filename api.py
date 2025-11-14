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


def generate_smart_selector(prompt: str) -> Dict[str, Any]:
    """Generate smart selector based on prompt - multiple strategies for robustness"""
    keywords = extract_keywords(prompt)
    prompt_lower = prompt.lower()
    
    # Calendar view selectors - use flexible text matching
    if "month" in prompt_lower:
        # Try multiple text variations - tagContainsSelector is case-insensitive
        # This will match "Month", "month", "Monthly", "Month View", etc.
        return create_selector("tagContainsSelector", "Month", case_sensitive=False)
    
    if "week" in prompt_lower:
        # Try multiple text variations
        return create_selector("tagContainsSelector", "Week", case_sensitive=False)
    
    if "day" in prompt_lower:
        return create_selector("tagContainsSelector", "Day", case_sensitive=False)
    
    # Priority: specific target words (month, week, etc.)
    priority_words = ["month", "week", "day", "year", "view"]
    for word in priority_words:
        if word in prompt_lower:
            # Use capitalized version for better matching
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
        actions.append({"action_type": "wait", "duration": 0.8})  # Longer wait for dynamic content
        actions.append({
            "action_type": "click",
            "selector": generate_smart_selector(prompt)
        })
        actions.append({"action_type": "wait", "duration": 2.0})  # Even longer wait for view change
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
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
