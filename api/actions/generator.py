"""Action sequence generation"""
from typing import Dict, Any, List
from .selectors import SelectorStrategy, create_selector
from ..utils.classification import TaskClassifier
from ..utils.keywords import extract_keywords


class ActionGenerator:
    """Generate action sequences based on task"""
    
    def __init__(self):
        self.classifier = TaskClassifier()
        self.selector_strategy = SelectorStrategy()
    
    def generate(self, prompt: str, url: str) -> List[Dict[str, Any]]:
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
            actions.append({"action_type": "wait", "duration": 1.0})  # Wait for dynamic content to stabilize
            
            # Generate multiple selector strategies for robustness
            selector_strategies = self.selector_strategy.get_strategies(prompt)
            
            # Try primary selector first
            actions.append({
                "action_type": "click",
                "selector": selector_strategies[0]
            })
            actions.append({"action_type": "wait", "duration": 0.3})  # Short wait to check if click worked
            
            # Add fallback selectors (try 2-3 most likely alternatives)
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

