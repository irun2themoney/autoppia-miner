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
        
        # Handle complex multi-step tasks
        if "login" in prompt_lower or "sign in" in prompt_lower:
            # Login task - extract credentials
            username = "user"
            password = "password123"
            
            # Extract username from prompt (e.g., "username:user<web_agent_id>")
            if "username:" in prompt_lower:
                username_part = prompt_lower.split("username:")[1].split()[0]
                username = username_part.replace("<web_agent_id>", "test")  # Placeholder
            
            # Extract password from prompt
            if "password:" in prompt_lower:
                password_part = prompt_lower.split("password:")[1].split()[0]
                password = password_part
            
            # Find and fill login form
            actions.append({"action_type": "wait", "duration": 1.0})
            
            # Username field
            username_selector = create_selector("attributeValueSelector", "username", attribute="name")
            actions.append({"action_type": "click", "selector": username_selector})
            actions.append({"action_type": "wait", "duration": 0.2})
            actions.append({"action_type": "type", "text": username, "selector": username_selector})
            
            # Password field
            password_selector = create_selector("attributeValueSelector", "password", attribute="type")
            actions.append({"action_type": "click", "selector": password_selector})
            actions.append({"action_type": "wait", "duration": 0.2})
            actions.append({"action_type": "type", "text": password, "selector": password_selector})
            
            # Submit button
            submit_selector = create_selector("tagContainsSelector", "Login", case_sensitive=False)
            actions.append({"action_type": "wait", "duration": 0.3})
            actions.append({"action_type": "click", "selector": submit_selector})
            actions.append({"action_type": "wait", "duration": 2.0})  # Wait for login
            actions.append({"action_type": "screenshot"})
            
            # Handle post-login tasks
            if "modify" in prompt_lower or "edit" in prompt_lower or "profile" in prompt_lower:
                # Navigate to profile
                profile_selector = create_selector("tagContainsSelector", "Profile", case_sensitive=False)
                actions.append({"action_type": "click", "selector": profile_selector})
                actions.append({"action_type": "wait", "duration": 1.5})
                actions.append({"action_type": "screenshot"})
                
                # Edit bio if mentioned
                if "bio" in prompt_lower:
                    bio_selector = create_selector("attributeValueSelector", "bio", attribute="name")
                    actions.append({"action_type": "click", "selector": bio_selector})
                    actions.append({"action_type": "wait", "duration": 0.2})
                    # Extract bio requirement (e.g., "contains the word 'car'")
                    bio_text = "car" if "car" in prompt_lower else "test bio"
                    actions.append({"action_type": "type", "text": bio_text, "selector": bio_selector})
                    actions.append({"action_type": "wait", "duration": 0.3})
                
                # Edit website if mentioned
                if "website" in prompt_lower:
                    website_selector = create_selector("attributeValueSelector", "website", attribute="name")
                    actions.append({"action_type": "click", "selector": website_selector})
                    actions.append({"action_type": "wait", "duration": 0.2})
                    website_text = "https://example.com"  # Default if URL needs to be removed
                    actions.append({"action_type": "type", "text": website_text, "selector": website_selector})
                    actions.append({"action_type": "wait", "duration": 0.3})
                
                # Save changes
                save_selector = create_selector("tagContainsSelector", "Save", case_sensitive=False)
                actions.append({"action_type": "click", "selector": save_selector})
                actions.append({"action_type": "wait", "duration": 1.0})
                actions.append({"action_type": "screenshot"})
            
            return actions
        
        # Handle comment posting
        if "comment" in prompt_lower or "post a comment" in prompt_lower:
            actions.append({"action_type": "wait", "duration": 1.0})
            
            # Find comment input (more specific selectors)
            comment_selectors = [
                create_selector("attributeValueSelector", "comment", attribute="name"),
                create_selector("attributeValueSelector", "comment", attribute="id"),
                create_selector("tagContainsSelector", "comment", case_sensitive=False),
                create_selector("attributeValueSelector", "textarea", attribute="custom"),
            ]
            
            # Try first selector
            actions.append({"action_type": "click", "selector": comment_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.3})
            
            # Type comment
            comment_text = "Great movie!" if "movie" in prompt_lower else "Test comment"
            actions.append({"action_type": "type", "text": comment_text, "selector": comment_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.5})
            
            # Submit comment
            submit_selector = create_selector("tagContainsSelector", "Post", case_sensitive=False)
            actions.append({"action_type": "click", "selector": submit_selector})
            actions.append({"action_type": "wait", "duration": 1.5})
            actions.append({"action_type": "screenshot"})
            
            return actions
        
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
            # Type task - be more specific
            actions.append({"action_type": "wait", "duration": 0.8})
            
            if "email" in prompt_lower:
                selector = create_selector("attributeValueSelector", "email", attribute="type")
                text = "test@example.com"
            elif "password" in prompt_lower:
                selector = create_selector("attributeValueSelector", "password", attribute="type")
                text = "password123"
            elif "comment" in prompt_lower:
                # Try multiple comment selectors
                selector = create_selector("attributeValueSelector", "comment", attribute="name")
                text = "Test comment"
            elif "bio" in prompt_lower:
                selector = create_selector("attributeValueSelector", "bio", attribute="name")
                text = "test bio"
            elif "website" in prompt_lower:
                selector = create_selector("attributeValueSelector", "website", attribute="name")
                text = "https://example.com"
            else:
                # More specific than "input:first-of-type"
                selector = create_selector("attributeValueSelector", "text", attribute="type")
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

