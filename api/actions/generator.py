"""Enhanced action sequence generation with expanded patterns"""
from typing import Dict, Any, List
from .selectors import SelectorStrategy, create_selector
from ..utils.classification import TaskClassifier
from ..utils.keywords import extract_keywords
from ..utils.task_parser import TaskParser
import re


class ActionGenerator:
    """Generate action sequences based on task - Enhanced with more patterns"""
    
    def __init__(self):
        self.classifier = TaskClassifier()
        self.selector_strategy = SelectorStrategy()
        self.task_parser = TaskParser()  # Enhanced parsing
    
    def generate(self, prompt: str, url: str) -> List[Dict[str, Any]]:
        """Generate action sequence based on prompt - Enhanced patterns"""
        actions = []
        prompt_lower = prompt.lower()
        
        # Parse task to extract all information
        parsed = self.task_parser.parse_task(prompt, url)
        task_url = parsed.get("url") or url
        credentials = parsed.get("credentials", {})
        text_to_type = parsed.get("text_to_type")
        target_element = parsed.get("target_element")
        task_type = parsed.get("task_type", "generic")
        
        # Navigate if URL provided
        if task_url:
            actions.append({"action_type": "navigate", "url": task_url})
            actions.append({"action_type": "wait", "duration": 1.5})  # Wait for page load
        
        # Initial screenshot
        actions.append({"action_type": "screenshot"})
        
        # Enhanced pattern matching with priority order
        
        # 1. LOGIN TASKS (highest priority - most specific)
        if task_type == "login" or "login" in prompt_lower or "sign in" in prompt_lower:
            actions.extend(self._generate_login_actions(parsed, prompt_lower))
            return actions
        
        # 2. FORM FILLING TASKS
        if task_type == "form" or any(w in prompt_lower for w in ["fill", "submit", "enter"]):
            actions.extend(self._generate_form_actions(parsed, prompt_lower))
            return actions
        
        # 3. MODIFY/EDIT TASKS
        if task_type == "modify" or any(w in prompt_lower for w in ["modify", "edit", "change", "update", "delete"]):
            actions.extend(self._generate_modify_actions(parsed, prompt_lower))
            return actions
        
        # 4. SEARCH TASKS
        if task_type == "search" or any(w in prompt_lower for w in ["search", "find", "look for"]):
            actions.extend(self._generate_search_actions(parsed, prompt_lower))
            return actions
        
        # 5. COMMENT/POST TASKS
        if any(w in prompt_lower for w in ["comment", "post", "reply", "write"]):
            actions.extend(self._generate_comment_actions(parsed, prompt_lower))
            return actions
        
        # 6. CLICK/SELECT TASKS (most common)
        if any(w in prompt_lower for w in ["click", "select", "choose", "switch", "toggle", "view", "open"]):
            actions.extend(self._generate_click_actions(parsed, prompt_lower, target_element))
            return actions
        
        # 7. TYPE/INPUT TASKS
        if any(w in prompt_lower for w in ["type", "enter", "input", "write"]):
            actions.extend(self._generate_type_actions(parsed, prompt_lower))
            return actions
        
        # 8. SCROLL TASKS
        if any(w in prompt_lower for w in ["scroll", "move down", "move up"]):
            actions.extend(self._generate_scroll_actions(parsed, prompt_lower))
            return actions
        
        # 9. EXTRACT/GET DATA TASKS
        if any(w in prompt_lower for w in ["extract", "get", "read", "retrieve", "fetch"]):
            actions.extend(self._generate_extract_actions(parsed, prompt_lower))
            return actions
        
        # 10. MULTI-STEP TASKS (handle "and", "then", "after")
        if any(w in prompt_lower for w in ["and", "then", "after", "before", "first", "next"]):
            actions.extend(self._generate_multistep_actions(parsed, prompt_lower))
            return actions
        
        # Default: Screenshot only
        actions.append({"action_type": "wait", "duration": 0.5})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_login_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate login action sequence"""
        actions = []
        credentials = parsed.get("credentials", {})
        
        username = credentials.get("username") or "user"
        password = credentials.get("password") or "password123"
        
        # Wait for page to be ready
        actions.append({"action_type": "wait", "duration": 1.0})
        
        # Username field - multiple selector strategies
        username_selectors = [
            create_selector("attributeValueSelector", "username", attribute="name"),
            create_selector("attributeValueSelector", "username", attribute="id"),
            create_selector("attributeValueSelector", "email", attribute="name"),  # Some sites use email
            create_selector("attributeValueSelector", "user", attribute="name"),
            create_selector("attributeValueSelector", "login", attribute="name"),
        ]
        
        actions.append({"action_type": "click", "selector": username_selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.2})
        actions.append({"action_type": "type", "text": username, "selector": username_selectors[0]})
        
        # Password field - multiple selector strategies
        password_selectors = [
            create_selector("attributeValueSelector", "password", attribute="type"),
            create_selector("attributeValueSelector", "password", attribute="name"),
            create_selector("attributeValueSelector", "password", attribute="id"),
        ]
        
        actions.append({"action_type": "wait", "duration": 0.3})
        actions.append({"action_type": "click", "selector": password_selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.2})
        actions.append({"action_type": "type", "text": password, "selector": password_selectors[0]})
        
        # Submit button - multiple strategies
        submit_selectors = [
            create_selector("tagContainsSelector", "Login", case_sensitive=False),
            create_selector("tagContainsSelector", "Sign In", case_sensitive=False),
            create_selector("tagContainsSelector", "Submit", case_sensitive=False),
            create_selector("attributeValueSelector", "submit", attribute="type"),
            create_selector("attributeValueSelector", "login", attribute="type"),
        ]
        
        actions.append({"action_type": "wait", "duration": 0.3})
        actions.append({"action_type": "click", "selector": submit_selectors[0]})
        actions.append({"action_type": "wait", "duration": 2.0})  # Wait for login
        actions.append({"action_type": "screenshot"})
        
        # Handle post-login tasks
        if any(w in prompt_lower for w in ["modify", "edit", "profile", "settings"]):
            actions.extend(self._generate_post_login_actions(parsed, prompt_lower))
        
        return actions
    
    def _generate_post_login_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate actions after login"""
        actions = []
        
        # Navigate to profile/settings if needed
        if "profile" in prompt_lower or "settings" in prompt_lower:
            profile_selectors = [
                create_selector("tagContainsSelector", "Profile", case_sensitive=False),
                create_selector("tagContainsSelector", "Settings", case_sensitive=False),
                create_selector("tagContainsSelector", "Account", case_sensitive=False),
            ]
            actions.append({"action_type": "wait", "duration": 1.0})
            actions.append({"action_type": "click", "selector": profile_selectors[0]})
            actions.append({"action_type": "wait", "duration": 1.5})
            actions.append({"action_type": "screenshot"})
        
        # Handle bio modification
        if "bio" in prompt_lower:
            bio_text = parsed.get("text_to_type") or "car" if "car" in prompt_lower else "test bio"
            bio_selectors = [
                create_selector("attributeValueSelector", "bio", attribute="name"),
                create_selector("attributeValueSelector", "bio", attribute="id"),
                create_selector("tagContainsSelector", "bio", case_sensitive=False),
            ]
            actions.append({"action_type": "click", "selector": bio_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.2})
            actions.append({"action_type": "type", "text": bio_text, "selector": bio_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.3})
        
        # Handle website modification
        if "website" in prompt_lower:
            website_text = parsed.get("text_to_type") or "https://example.com"
            website_selectors = [
                create_selector("attributeValueSelector", "website", attribute="name"),
                create_selector("attributeValueSelector", "url", attribute="name"),
                create_selector("attributeValueSelector", "website", attribute="id"),
            ]
            actions.append({"action_type": "click", "selector": website_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.2})
            # Clear field first if needed
            actions.append({"action_type": "type", "text": website_text, "selector": website_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.3})
        
        # Save changes
        save_selectors = [
            create_selector("tagContainsSelector", "Save", case_sensitive=False),
            create_selector("tagContainsSelector", "Update", case_sensitive=False),
            create_selector("tagContainsSelector", "Submit", case_sensitive=False),
            create_selector("attributeValueSelector", "submit", attribute="type"),
        ]
        actions.append({"action_type": "click", "selector": save_selectors[0]})
        actions.append({"action_type": "wait", "duration": 1.5})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_form_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate form filling actions"""
        actions = []
        credentials = parsed.get("credentials", {})
        text_to_type = parsed.get("text_to_type")
        
        actions.append({"action_type": "wait", "duration": 1.0})
        
        # Extract field-value pairs from prompt
        field_patterns = {
            "name": r"name[:\s]+['\"]?([^'\"]+)['\"]?",
            "email": r"email[:\s]+['\"]?([^'\"]+)['\"]?",
            "phone": r"phone[:\s]+['\"]?([^'\"]+)['\"]?",
            "message": r"message[:\s]+['\"]?([^'\"]+)['\"]?",
            "subject": r"subject[:\s]+['\"]?([^'\"]+)['\"]?",
        }
        
        fields_to_fill = []
        for field_name, pattern in field_patterns.items():
            match = re.search(pattern, prompt_lower, re.IGNORECASE)
            if match:
                fields_to_fill.append((field_name, match.group(1)))
        
        # Fill each field
        for field_name, field_value in fields_to_fill:
            field_selectors = [
                create_selector("attributeValueSelector", field_name, attribute="name"),
                create_selector("attributeValueSelector", field_name, attribute="id"),
                create_selector("attributeValueSelector", field_name, attribute="placeholder"),
            ]
            actions.append({"action_type": "click", "selector": field_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.2})
            actions.append({"action_type": "type", "text": field_value, "selector": field_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.3})
        
        # Submit form
        submit_selectors = [
            create_selector("tagContainsSelector", "Submit", case_sensitive=False),
            create_selector("tagContainsSelector", "Send", case_sensitive=False),
            create_selector("attributeValueSelector", "submit", attribute="type"),
        ]
        actions.append({"action_type": "click", "selector": submit_selectors[0]})
        actions.append({"action_type": "wait", "duration": 1.5})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_modify_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate modify/edit actions"""
        actions = []
        target_element = parsed.get("target_element")
        text_to_type = parsed.get("text_to_type")
        
        actions.append({"action_type": "wait", "duration": 1.0})
        
        # Find element to modify
        if target_element:
            element_selectors = self.selector_strategy.get_strategies(f"click {target_element}")
            actions.append({"action_type": "click", "selector": element_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.5})
        
        # Type new value
        if text_to_type:
            # Try to find input/textarea
            input_selectors = [
                create_selector("attributeValueSelector", "input", attribute="type"),
                create_selector("tagContainsSelector", "textarea", case_sensitive=False),
            ]
            actions.append({"action_type": "click", "selector": input_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.2})
            actions.append({"action_type": "type", "text": text_to_type, "selector": input_selectors[0]})
            actions.append({"action_type": "wait", "duration": 0.3})
        
        # Save changes
        save_selectors = [
            create_selector("tagContainsSelector", "Save", case_sensitive=False),
            create_selector("tagContainsSelector", "Update", case_sensitive=False),
        ]
        actions.append({"action_type": "click", "selector": save_selectors[0]})
        actions.append({"action_type": "wait", "duration": 1.0})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_search_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate search actions"""
        actions = []
        
        # Extract search query
        search_query = parsed.get("text_to_type") or "test query"
        if "for" in prompt_lower:
            # Extract text after "for"
            parts = prompt_lower.split("for", 1)
            if len(parts) > 1:
                query_part = parts[1].strip()
                # Remove quotes if present
                query_part = query_part.strip("'\"")
                if query_part:
                    search_query = query_part.split()[0]  # Take first word
        
        actions.append({"action_type": "wait", "duration": 1.0})
        
        # Search input - multiple strategies
        search_selectors = [
            create_selector("attributeValueSelector", "search", attribute="type"),
            create_selector("attributeValueSelector", "search", attribute="name"),
            create_selector("attributeValueSelector", "q", attribute="name"),  # Common search param
            create_selector("attributeValueSelector", "query", attribute="name"),
        ]
        
        actions.append({"action_type": "click", "selector": search_selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.2})
        actions.append({"action_type": "type", "text": search_query, "selector": search_selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.5})
        
        # Search button
        search_button_selectors = [
            create_selector("tagContainsSelector", "Search", case_sensitive=False),
            create_selector("attributeValueSelector", "submit", attribute="type"),
            create_selector("tagContainsSelector", "Go", case_sensitive=False),
        ]
        actions.append({"action_type": "click", "selector": search_button_selectors[0]})
        actions.append({"action_type": "wait", "duration": 2.0})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_comment_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate comment/post actions"""
        actions = []
        text_to_type = parsed.get("text_to_type") or "Great movie!" if "movie" in prompt_lower else "Test comment"
        
        actions.append({"action_type": "wait", "duration": 1.0})
        
        # Comment input - multiple strategies
        comment_selectors = [
            create_selector("attributeValueSelector", "comment", attribute="name"),
            create_selector("attributeValueSelector", "comment", attribute="id"),
            create_selector("tagContainsSelector", "comment", case_sensitive=False),
            create_selector("attributeValueSelector", "textarea", attribute="custom"),
            create_selector("attributeValueSelector", "message", attribute="name"),
        ]
        
        actions.append({"action_type": "click", "selector": comment_selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.3})
        actions.append({"action_type": "type", "text": text_to_type, "selector": comment_selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.5})
        
        # Submit comment
        submit_selectors = [
            create_selector("tagContainsSelector", "Post", case_sensitive=False),
            create_selector("tagContainsSelector", "Comment", case_sensitive=False),
            create_selector("tagContainsSelector", "Submit", case_sensitive=False),
            create_selector("attributeValueSelector", "submit", attribute="type"),
        ]
        actions.append({"action_type": "click", "selector": submit_selectors[0]})
        actions.append({"action_type": "wait", "duration": 1.5})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_click_actions(self, parsed: Dict[str, Any], prompt_lower: str, target_element: str = None) -> List[Dict[str, Any]]:
        """Generate click actions with enhanced selector strategies"""
        actions = []
        
        actions.append({"action_type": "wait", "duration": 1.0})  # Wait for dynamic content
        
        # Generate multiple selector strategies
        if target_element:
            selector_strategies = self.selector_strategy.get_strategies(f"click {target_element}")
        else:
            # Extract target from prompt
            selector_strategies = self.selector_strategy.get_strategies(prompt_lower)
        
        # Use primary selector
        if selector_strategies:
            actions.append({"action_type": "click", "selector": selector_strategies[0]})
            actions.append({"action_type": "wait", "duration": 0.3})
            
            # Add fallback selectors (try 2-3 most likely)
            for selector in selector_strategies[1:3]:
                actions.append({"action_type": "click", "selector": selector})
                actions.append({"action_type": "wait", "duration": 0.3})
        
        actions.append({"action_type": "wait", "duration": 2.0})  # Wait for view change
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_type_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate type/input actions"""
        actions = []
        text_to_type = parsed.get("text_to_type") or "test"
        
        # Determine field type
        field_type = "text"
        if "email" in prompt_lower:
            field_type = "email"
            text_to_type = parsed.get("credentials", {}).get("email") or "test@example.com"
        elif "password" in prompt_lower:
            field_type = "password"
            text_to_type = parsed.get("credentials", {}).get("password") or "password123"
        elif "comment" in prompt_lower:
            field_type = "comment"
            text_to_type = text_to_type or "Test comment"
        elif "bio" in prompt_lower:
            field_type = "bio"
            text_to_type = text_to_type or "test bio"
        elif "website" in prompt_lower:
            field_type = "website"
            text_to_type = text_to_type or "https://example.com"
        
        actions.append({"action_type": "wait", "duration": 0.8})
        
        # Generate selectors for field type
        field_selectors = {
            "email": [
                create_selector("attributeValueSelector", "email", attribute="type"),
                create_selector("attributeValueSelector", "email", attribute="name"),
            ],
            "password": [
                create_selector("attributeValueSelector", "password", attribute="type"),
                create_selector("attributeValueSelector", "password", attribute="name"),
            ],
            "comment": [
                create_selector("attributeValueSelector", "comment", attribute="name"),
                create_selector("tagContainsSelector", "comment", case_sensitive=False),
            ],
            "bio": [
                create_selector("attributeValueSelector", "bio", attribute="name"),
                create_selector("attributeValueSelector", "bio", attribute="id"),
            ],
            "website": [
                create_selector("attributeValueSelector", "website", attribute="name"),
                create_selector("attributeValueSelector", "url", attribute="name"),
            ],
            "text": [
                create_selector("attributeValueSelector", "text", attribute="type"),
                create_selector("attributeValueSelector", "input", attribute="type"),
            ],
        }
        
        selectors = field_selectors.get(field_type, field_selectors["text"])
        actions.append({"action_type": "click", "selector": selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.2})
        actions.append({"action_type": "type", "text": text_to_type, "selector": selectors[0]})
        actions.append({"action_type": "wait", "duration": 0.5})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_scroll_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate scroll actions"""
        actions = []
        
        direction = "down"
        if "up" in prompt_lower:
            direction = "up"
        
        pixels = 500
        if "more" in prompt_lower or "further" in prompt_lower:
            pixels = 1000
        
        actions.append({"action_type": "wait", "duration": 0.5})
        actions.append({"action_type": "scroll", "direction": direction, "pixels": pixels})
        actions.append({"action_type": "wait", "duration": 1.0})
        actions.append({"action_type": "screenshot"})
        
        return actions
    
    def _generate_extract_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate extract/get data actions"""
        actions = []
        
        # For extraction, we mainly need to navigate and screenshot
        # The actual extraction happens in post-processing
        actions.append({"action_type": "wait", "duration": 1.0})
        actions.append({"action_type": "screenshot"})
        actions.append({"action_type": "wait", "duration": 0.5})
        actions.append({"action_type": "screenshot"})  # Multiple screenshots for data
        
        return actions
    
    def _generate_multistep_actions(self, parsed: Dict[str, Any], prompt_lower: str) -> List[Dict[str, Any]]:
        """Generate multi-step actions"""
        actions = []
        
        # Split by common connectors
        steps = re.split(r"\b(and|then|after|before|first|next)\b", prompt_lower)
        steps = [s.strip() for s in steps if s.strip() and s.lower() not in ["and", "then", "after", "before", "first", "next"]]
        
        # Generate actions for each step
        for i, step in enumerate(steps[:3]):  # Limit to 3 steps
            if i > 0:
                actions.append({"action_type": "wait", "duration": 1.0})
            
            # Parse step
            step_parsed = self.task_parser.parse_task(step, parsed.get("url", ""))
            
            # Generate actions for this step
            if "click" in step.lower():
                actions.extend(self._generate_click_actions(step_parsed, step.lower(), step_parsed.get("target_element")))
            elif "type" in step.lower() or "enter" in step.lower():
                actions.extend(self._generate_type_actions(step_parsed, step.lower()))
            elif "search" in step.lower():
                actions.extend(self._generate_search_actions(step_parsed, step.lower()))
            else:
                # Generic step
                actions.append({"action_type": "wait", "duration": 0.5})
                actions.append({"action_type": "screenshot"})
        
        return actions
