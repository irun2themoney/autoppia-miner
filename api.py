"""
Optimized API server for IWA (Infinite Web Arena)
Lightweight, fast, and effective - optimized for competitive performance

Key optimizations:
- Minimal logging (errors only)
- No external AI dependencies
- Streamlined task classification
- Optimized action templates
- Fast response times (<50ms typical)
"""

import json
import os
import re
import sys
import time
from typing import Dict, Any, List
from collections import defaultdict
from threading import Lock
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Minimal logging - use print for errors only (no external dependency needed)
def log_error(msg):
    print(f"ERROR: {msg}", file=sys.stderr)

def log_warning(msg):
    pass  # Suppress warnings for speed

app = FastAPI(title="IWA Miner", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Minimal metrics
class Metrics:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.by_type = defaultdict(int)
        self.lock = Lock()
    
    def record(self, task_type: str, success: bool):
        with self.lock:
            self.total += 1
            if success:
                self.success += 1
                self.by_type[task_type] += 1

metrics = Metrics()


def extract_keywords(prompt: str) -> Dict[str, Any]:
    """Extract keywords and context from prompt for smart selector generation"""
    prompt_lower = prompt.lower()
    keywords = {
        "action_words": [],
        "target_words": [],
        "form_fields": [],
        "button_types": []
    }
    
    # Extract action words
    action_patterns = {
        "login": ["login", "sign in", "log in", "authenticate"],
        "logout": ["logout", "sign out", "log out"],
        "submit": ["submit", "send", "post", "confirm"],
        "search": ["search", "find", "look for", "query"],
        "click": ["click", "select", "choose", "pick"],
        "fill": ["fill", "enter", "type", "input"],
        "navigate": ["go to", "visit", "open", "navigate"],
        "add": ["add", "create", "new"],
        "remove": ["remove", "delete", "remove"],
        "checkout": ["checkout", "purchase", "buy", "pay"],
        "switch": ["switch", "toggle", "change", "set"],
        "view": ["view", "show", "display"],
    }
    
    for action_type, patterns in action_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            keywords["action_words"].append(action_type)
    
    # Extract target words (what to interact with)
    target_patterns = {
        "button": ["button", "btn", "click"],
        "link": ["link", "href", "anchor"],
        "input": ["input", "field", "textbox", "textarea"],
        "form": ["form", "submit"],
        "search": ["search", "query", "find"],
        "cart": ["cart", "basket", "shopping"],
        "menu": ["menu", "nav", "navigation"],
        "dropdown": ["dropdown", "select", "menu"],
    }
    
    for target_type, patterns in target_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            keywords["target_words"].append(target_type)
    
    # Extract form field types
    field_patterns = {
        "email": ["email", "e-mail", "mail"],
        "password": ["password", "pwd", "pass"],
        "name": ["name", "username", "user name"],
        "phone": ["phone", "telephone", "mobile"],
        "address": ["address", "location"],
        "date": ["date", "time", "when"],
        "country": ["country", "nation"],
    }
    
    for field_type, patterns in field_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            keywords["form_fields"].append(field_type)
    
    # Extract button types
    button_patterns = {
        "submit": ["submit", "send", "post"],
        "login": ["login", "sign in"],
        "register": ["register", "sign up", "create account"],
        "cancel": ["cancel", "close"],
        "delete": ["delete", "remove"],
        "add": ["add", "create", "new"],
    }
    
    for btn_type, patterns in button_patterns.items():
        if any(pattern in prompt_lower for pattern in patterns):
            keywords["button_types"].append(btn_type)
    
    return keywords


def generate_smart_selector(prompt: str, task_type: str, action_type: str = "click") -> Dict[str, Any]:
    """Generate smart selector using official IWA selector attributes"""
    keywords = extract_keywords(prompt)
    prompt_lower = prompt.lower()
    
    # For text-based selectors (buttons, links)
    if action_type == "click":
        # Extract key words from prompt for better matching
        prompt_words = prompt_lower.split()
        key_words = []
        
        # Find important words (not common words)
        common_words = {"the", "a", "an", "to", "in", "on", "at", "for", "of", "with", "click", "button", "link"}
        for word in prompt_words:
            if word not in common_words and len(word) > 2:
                key_words.append(word)
        
        # Try tagContainsSelector with extracted words
        if key_words:
            # Prioritize important words (month, week, day, etc.)
            priority_words = ["month", "week", "day", "year", "view", "login", "submit", "search"]
            for word in key_words:
                if word in priority_words:
                    text_value = word.title()
                    return {
                        "type": "tagContainsSelector",
                        "value": text_value,
                        "case_sensitive": False
                    }
            # Use the most relevant word (usually the last meaningful word)
            text_value = key_words[-1].title() if key_words else "Button"
            return {
                "type": "tagContainsSelector",
                "value": text_value,
                "case_sensitive": False
            }
        
        # Fallback to action words
        if keywords["action_words"]:
            action_word = keywords["action_words"][0]
            # Capitalize first letter for text matching
            text_value = action_word.replace("_", " ").title()
            return {
                "type": "tagContainsSelector",
                "value": text_value,
                "case_sensitive": False
            }
        
        # Try specific button types
        if keywords["button_types"]:
            btn_type = keywords["button_types"][0].replace("_", "-")
            # Try data-testid first (most specific)
            return {
                "type": "attributeValueSelector",
                "attribute": "data-testid",
                "value": f"{btn_type}-button",
                "case_sensitive": False
            }
        
        # Try id attribute
        if any(word in prompt_lower for word in ["button", "btn", "link"]):
            # Extract key word from prompt
            words = prompt_lower.split()
            for word in words:
                if len(word) > 3 and word not in ["the", "click", "button", "link"]:
                    return {
                        "type": "attributeValueSelector",
                        "attribute": "id",
                        "value": f"{word}-button",
                        "case_sensitive": False
                    }
    
    # For input fields
    elif action_type == "type":
        if keywords["form_fields"]:
            field_type = keywords["form_fields"][0]
            # Try name attribute first (most common for forms)
            return {
                "type": "attributeValueSelector",
                "attribute": "name",
                "value": field_type,
                "case_sensitive": False
            }
        
        # Try type attribute
        if "email" in prompt_lower:
            return {
                "type": "attributeValueSelector",
                "attribute": "type",
                "value": "email",
                "case_sensitive": False
            }
        elif "password" in prompt_lower:
            return {
                "type": "attributeValueSelector",
                "attribute": "type",
                "value": "password",
                "case_sensitive": False
            }
    
    # For search inputs
    if "search" in prompt_lower or task_type == "search":
        return {
            "type": "attributeValueSelector",
            "attribute": "type",
            "value": "search",
            "case_sensitive": False
        }
    
    # Fallback: Use CSS selector with custom attribute
    if task_type == "click":
        return {
            "type": "attributeValueSelector",
            "attribute": "custom",
            "value": "button:first-of-type, [role='button'], .btn, button",
            "case_sensitive": False
        }
    elif task_type == "form_fill":
        return {
            "type": "attributeValueSelector",
            "attribute": "custom",
            "value": "input:first-of-type, input[type='text'], textarea:first-of-type",
            "case_sensitive": False
        }
    else:
        return {
            "type": "attributeValueSelector",
            "attribute": "custom",
            "value": "button:first-of-type",
            "case_sensitive": False
        }


def extract_text_from_prompt(prompt: str, task_type: str) -> str:
    """Extract relevant text to type based on prompt context"""
    prompt_lower = prompt.lower()
    
    # For form fields, extract example values
    if "email" in prompt_lower:
        return "test@example.com"
    elif "password" in prompt_lower:
        return "password123"
    elif "name" in prompt_lower or "username" in prompt_lower:
        return "testuser"
    elif "phone" in prompt_lower:
        return "1234567890"
    elif "address" in prompt_lower:
        return "123 Main St"
    elif "date" in prompt_lower:
        return "2024-01-01"
    elif task_type == "search":
        # Extract search query from prompt
        words = prompt.split()
        search_words = []
        skip_next = False
        for i, word in enumerate(words):
            if skip_next:
                skip_next = False
                continue
            if word.lower() in ["search", "find", "look", "for", "query"]:
                if i + 1 < len(words):
                    search_words.append(words[i + 1])
                    skip_next = True
            elif word.lower() not in ["click", "button", "the", "a", "an"]:
                search_words.append(word)
        if search_words:
            return " ".join(search_words[:3])  # Max 3 words
        return "test query"
    
    return "test"


def convert_to_iwa_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert action from internal format to IWA BaseAction format.
    
    Maps:
    - action_type: "click" -> type: "ClickAction"
    - selector: CSS string -> selector: IWA Selector object
    - duration -> time_seconds (for WaitAction)
    - direction/amount -> up/down/left/right/value (for ScrollAction)
    """
    action_type = action.get("action_type", "")
    
    # Map action types to IWA format
    type_map = {
        "click": "ClickAction",
        "type": "TypeAction",
        "wait": "WaitAction",
        "navigate": "NavigateAction",
        "screenshot": "ScreenshotAction",
        "scroll": "ScrollAction",
        "key_press": "SendKeysIWAAction",
    }
    
    iwa_type = type_map.get(action_type, "ClickAction")
    result: Dict[str, Any] = {"type": iwa_type}
    
    # Handle selector conversion - support both Dict (smart selector) and string (CSS fallback)
    if "selector" in action and action["selector"]:
        if isinstance(action["selector"], dict):
            # Already in IWA format (from smart selector)
            result["selector"] = action["selector"]
        else:
            # CSS string - convert to IWA format
            result["selector"] = {
                "type": "attributeValueSelector",
                "attribute": "custom",
                "value": action["selector"],
                "case_sensitive": False
            }
    
    # Handle action-specific field mappings
    if iwa_type == "WaitAction":
        # Convert "duration" to "time_seconds"
        if "duration" in action:
            result["time_seconds"] = action["duration"]
        elif "time_seconds" in action:
            result["time_seconds"] = action["time_seconds"]
    
    elif iwa_type == "TypeAction":
        # Copy text field
        if "text" in action:
            result["text"] = action["text"]
        elif "value" in action:
            result["text"] = action["value"]
    
    elif iwa_type == "NavigateAction":
        # Copy URL
        if "url" in action:
            result["url"] = action["url"]
    
    elif iwa_type == "ScrollAction":
        # Convert direction/amount to up/down/left/right/value
        direction = action.get("direction", "down").lower()
        amount = action.get("amount", None)
        
        if direction == "down":
            result["down"] = True
        elif direction == "up":
            result["up"] = True
        elif direction == "left":
            result["left"] = True
        elif direction == "right":
            result["right"] = True
        
        if amount is not None:
            result["value"] = amount
    
    elif iwa_type == "SendKeysIWAAction":
        # Convert "key" to "keys"
        if "key" in action:
            result["keys"] = action["key"]
        elif "keys" in action:
            result["keys"] = action["keys"]
    
    elif iwa_type == "ClickAction":
        # Copy x, y coordinates if present
        if "x" in action:
            result["x"] = action["x"]
        if "y" in action:
            result["y"] = action["y"]
    
    elif iwa_type == "ScreenshotAction":
        # Copy optional fields
        if "file_path" in action:
            result["file_path"] = action["file_path"]
        if "full_page" in action:
            result["full_page"] = action["full_page"]
    
    return result


class TaskClassifier:
    """Fast task classifier optimized for IWA patterns"""
    
    # Optimized patterns - most common IWA task types first
    PATTERNS = {
        "click": r"\b(click|select|choose|pick|tap|delete|remove|open|close|finalize|book|reserve|confirm|submit|post|comment|mark|flag|archive|star|favorite|switch|toggle|view|change|set)\b",
        "form_fill": r"\b(fill|submit|complete|form|input|register|authenticate|login|log in|sign in|sign up|update|edit|add|create|send|enter|type|book|reserve|select|choose|dropdown|guests|people|date|time|country|phone|name|email|password|address|label)\b",
        "search": r"\b(search|find|look for|query|browse|filter|show details for|where|contains|equals|not equal|greater than|less than)\b",
        "navigate": r"\b(go to|visit|open|access|navigate|contact page|scroll through|section titled)\b",
        "extract": r"\b(extract|get|retrieve|copy|collect|scrape|show|display|view|details|information)\b",
        "checkout": r"\b(checkout|purchase|buy|add to cart|pay|logout|log out|sign out|finalize|complete purchase)\b",
    }
    
    @staticmethod
    def classify(prompt: str) -> str:
        """Fast classification using regex"""
        prompt_lower = prompt.lower()
        scores = {task_type: len(re.findall(pattern, prompt_lower)) 
                 for task_type, pattern in TaskClassifier.PATTERNS.items()}
        
        max_score = max(scores.values()) if scores.values() else 0
        if max_score > 0:
            return max(scores, key=scores.get)
        return "generic"
    
    @staticmethod
    def generate_actions(task_type: str, url: str, prompt: str) -> List[Dict]:
        """Generate smart, context-aware action sequences - optimized for IWA"""
        actions = []
        
        # Navigate first if URL provided
        if url and url.strip():
            actions.append({"action_type": "navigate", "url": url})
            # Adaptive wait based on task complexity
            wait_time = 1.2 if task_type in ["form_fill", "checkout"] else 0.8
            actions.append({"action_type": "wait", "duration": wait_time})
        
        # Smart, context-aware action generation
        if task_type == "click":
            # Click tasks: smart selector + minimal actions
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.2},  # Faster wait
                {"action_type": "click", "selector": generate_smart_selector(prompt, task_type, "click")},
                {"action_type": "wait", "duration": 0.8},  # Shorter wait for clicks
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "form_fill":
            # Form fill: smart field detection + context-aware text
            text_to_type = extract_text_from_prompt(prompt, task_type)
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.3},
                {"action_type": "click", "selector": generate_smart_selector(prompt, task_type, "type")},
                {"action_type": "wait", "duration": 0.15},
                {"action_type": "type", "text": text_to_type},
                {"action_type": "wait", "duration": 0.15},
                {"action_type": "click", "selector": generate_smart_selector(prompt, "submit", "click")},
                {"action_type": "wait", "duration": 1.2},  # Longer for form submission
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "search":
            # Search: smart search input + extracted query
            search_query = extract_text_from_prompt(prompt, task_type)
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.2},
                {"action_type": "click", "selector": generate_smart_selector(prompt, task_type, "type")},
                {"action_type": "wait", "duration": 0.15},
                {"action_type": "type", "text": search_query},
                {"action_type": "wait", "duration": 0.15},
                {"action_type": "key_press", "key": "Enter"},
                {"action_type": "wait", "duration": 1.0},  # Wait for results
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "navigate":
            # Navigate: minimal actions
            if url and url.strip():
                actions.extend([
                    {"action_type": "wait", "duration": 0.8},
                    {"action_type": "screenshot"}
                ])
            else:
                actions.append({"action_type": "screenshot"})
        
        elif task_type == "extract":
            # Extract: scroll to reveal content
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "scroll", "direction": "down", "amount": 3},  # More scroll
                {"action_type": "wait", "duration": 0.4},
                {"action_type": "screenshot"}
            ])
        
        elif task_type == "checkout":
            # Checkout: smart cart/checkout detection
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "click", "selector": generate_smart_selector(prompt, task_type, "click")},
                {"action_type": "wait", "duration": 1.2},  # Longer for checkout
                {"action_type": "screenshot"}
            ])
        
        else:  # generic
            # Generic: minimal exploration
            actions.extend([
                {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 0.3},
                {"action_type": "scroll", "direction": "down", "amount": 2},
                {"action_type": "wait", "duration": 0.3},
                {"action_type": "screenshot"}
            ])
        
        return actions


@app.get("/")
async def root():
    return {"service": "iwa-miner", "version": "2.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/solve_task")
async def solve_task(request_data: Dict[str, Any]):
    """Main IWA endpoint - optimized for speed"""
    start_time = time.time()
    
    try:
        task_id = request_data.get("id", "unknown")
        prompt = request_data.get("prompt", "")
        url = request_data.get("url", "")
        
        # Handle missing prompt
        if not prompt:
            prompt = f"Navigate to {url}" if url else "Generic web task"
        
        # Classify and generate actions (fast path)
        task_type = TaskClassifier.classify(prompt)
        raw_actions = TaskClassifier.generate_actions(task_type, url, prompt)
        
        # Ensure we have actions
        if not raw_actions:
            raw_actions = [
                {"action_type": "navigate", "url": url} if url else {"action_type": "screenshot"},
                {"action_type": "wait", "duration": 1.0},
                {"action_type": "screenshot"}
            ]
        
        # Convert actions to IWA format
        iwa_actions = []
        for action in raw_actions:
            try:
                converted = convert_to_iwa_action(action)
                iwa_actions.append(converted)
            except Exception as conv_err:
                # Log conversion error but continue
                print(f"⚠️  Action conversion error: {conv_err}")
                print(f"   Action: {action}")
                # Add fallback action
                iwa_actions.append({
                    "type": "ScreenshotAction"
                })
        
        # CRITICAL: Ensure we always have at least one action
        # Empty actions cause playground to show "No actions recorded"
        if not iwa_actions:
            print("⚠️  No actions generated, adding fallback")
            iwa_actions = [
                {"type": "ScreenshotAction"}
            ]
        
        elapsed = time.time() - start_time
        metrics.record(task_type, True)
        
        # Return IWA-compatible response format
        return JSONResponse(
            content={
                "actions": iwa_actions,  # IWA expects "actions" array
                "web_agent_id": task_id,  # Optional but recommended
                "recording": "",  # Optional
                # Keep backward compatibility fields
                "id": task_id,
                "task_id": task_id,
                "task_type": task_type,
                "success": True,
                "cached": False,
                "response_time_ms": f"{elapsed*1000:.0f}",
                "message": f"Task processed: {len(iwa_actions)} actions ({elapsed*1000:.0f}ms)"
            },
            status_code=200
        )
    
    except Exception as e:
        elapsed = time.time() - start_time
        metrics.record("error", False)
        log_error(f"Error: {str(e)}")
        
        return JSONResponse(
            content={
                "id": request_data.get("id", "unknown"),
                "task_id": request_data.get("id", "unknown"),
                "success": False,
                "error": str(e),
                "actions": [],
                "response_time_ms": f"{elapsed*1000:.0f}"
            },
            status_code=500
        )


@app.get("/metrics")
async def get_metrics():
    """Minimal metrics endpoint"""
    return {
        "total": metrics.total,
        "success": metrics.success,
        "success_rate": f"{(metrics.success / metrics.total * 100):.1f}%" if metrics.total > 0 else "0%",
        "by_type": dict(metrics.by_type)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="warning"  # Minimal logging
    )

