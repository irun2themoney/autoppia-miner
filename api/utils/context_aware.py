"""Context-aware action generation - understands page context and adapts strategy"""
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


class ContextAwareAgent:
    """
    Context-aware agent that understands page context and adapts action strategy
    
    Detects:
    - Page type (login, form, dashboard, search, etc.)
    - Page state (loaded, ready, etc.)
    - Element visibility
    - Action context
    """
    
    # URL patterns for context detection
    URL_PATTERNS = {
        "login": [
            r"/login",
            r"/signin",
            r"/sign-in",
            r"/auth",
            r"/authenticate",
        ],
        "form": [
            r"/form",
            r"/submit",
            r"/register",
            r"/signup",
            r"/contact",
        ],
        "dashboard": [
            r"/dashboard",
            r"/home",
            r"/profile",
            r"/account",
            r"/settings",
        ],
        "search": [
            r"/search",
            r"/find",
            r"/query",
        ],
        "calendar": [
            r"/calendar",
            r"/events",
            r"/schedule",
        ],
    }
    
    # Prompt patterns for context detection
    PROMPT_PATTERNS = {
        "login": [
            r"\b(login|sign in|authenticate|log in)\b",
            r"username.*password",
            r"credentials",
        ],
        "form": [
            r"\b(fill|submit|enter|form)\b",
            r"field.*value",
        ],
        "dashboard": [
            r"\b(dashboard|home|profile|account|settings)\b",
        ],
        "search": [
            r"\b(search|find|look for|query)\b",
        ],
        "calendar": [
            r"\b(calendar|event|schedule|date|month view)\b",
        ],
        "modal": [
            r"\b(modal|dialog|popup|close modal|dismiss)\b",
        ],
        "tab": [
            r"\b(tab|switch tab|open tab)\b",
        ],
    }
    
    def __init__(self):
        self.context_history = []  # Track context through multi-step flows
        self.page_state = {}  # Track current page state
    
    def detect_context(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        Detect page context from URL and prompt
        
        Returns:
            Dict with context information:
            - page_type: login, form, dashboard, search, calendar, generic
            - is_login_page: bool
            - is_form_page: bool
            - is_dashboard: bool
            - requires_navigation: bool
            - action_context: click, type, submit, etc.
        """
        context = {
            "page_type": "generic",
            "is_login_page": False,
            "is_form_page": False,
            "is_dashboard": False,
            "is_search_page": False,
            "is_calendar_page": False,
            "is_modal": False,
            "is_tab": False,
            "requires_navigation": True,
            "action_context": "generic",
        }
        
        url_lower = url.lower() if url else ""
        prompt_lower = prompt.lower()
        
        # Detect page type from URL
        for page_type, patterns in self.URL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower, re.IGNORECASE):
                    context["page_type"] = page_type
                    context[f"is_{page_type}_page"] = True
                    break
            if context["page_type"] != "generic":
                break
        
        # Detect page type from prompt (if URL didn't match)
        if context["page_type"] == "generic":
            for page_type, patterns in self.PROMPT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, prompt_lower, re.IGNORECASE):
                        context["page_type"] = page_type
                        if page_type in ["login", "form", "dashboard", "search", "calendar"]:
                            context[f"is_{page_type}_page"] = True
                        elif page_type == "modal":
                            context["is_modal"] = True
                        elif page_type == "tab":
                            context["is_tab"] = True
                        break
                if context["page_type"] != "generic":
                    break
        
        # Detect action context
        if any(word in prompt_lower for word in ["click", "select", "choose"]):
            context["action_context"] = "click"
        elif any(word in prompt_lower for word in ["type", "enter", "input", "fill"]):
            context["action_context"] = "type"
        elif any(word in prompt_lower for word in ["submit", "save", "send"]):
            context["action_context"] = "submit"
        elif any(word in prompt_lower for word in ["navigate", "go to", "open"]):
            context["action_context"] = "navigate"
        elif any(word in prompt_lower for word in ["search", "find"]):
            context["action_context"] = "search"
        
        # Determine if navigation is needed
        # If we're already on the right page type, might not need navigation
        if context["page_type"] != "generic" and url:
            # Check if URL matches the expected page type
            context["requires_navigation"] = not self._url_matches_context(url, context)
        
        return context
    
    def _url_matches_context(self, url: str, context: Dict[str, Any]) -> bool:
        """Check if URL matches the detected context"""
        url_lower = url.lower()
        page_type = context.get("page_type", "generic")
        
        if page_type == "generic":
            return True  # Generic pages don't need specific URL matching
        
        # Check if URL contains patterns for this page type
        patterns = self.URL_PATTERNS.get(page_type, [])
        for pattern in patterns:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return True
        
        return False
    
    def adapt_strategy(self, context: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """
        Adapt action strategy based on context
        
        Returns:
            Strategy dict with:
            - wait_after_navigation: float
            - wait_between_actions: float
            - screenshot_frequency: str (always, after_important, minimal)
            - selector_strategy: str (aggressive, conservative, balanced)
            - retry_strategy: str (none, once, multiple)
        """
        strategy = {
            "wait_after_navigation": 1.5,
            "wait_between_actions": 0.5,
            "screenshot_frequency": "after_important",
            "selector_strategy": "balanced",
            "retry_strategy": "once",
        }
        
        page_type = context.get("page_type", "generic")
        action_context = context.get("action_context", "generic")
        
        # Adapt based on page type
        if page_type == "login":
            strategy["wait_after_navigation"] = 2.0  # Login pages often have redirects
            strategy["wait_between_actions"] = 0.3  # Faster typing
            strategy["screenshot_frequency"] = "always"  # Important to capture login state
            strategy["selector_strategy"] = "aggressive"  # Try multiple selectors
            strategy["retry_strategy"] = "multiple"  # Login is critical
        
        elif page_type == "form":
            strategy["wait_after_navigation"] = 1.5
            strategy["wait_between_actions"] = 0.3  # Fast form filling
            strategy["screenshot_frequency"] = "after_important"
            strategy["selector_strategy"] = "balanced"
            strategy["retry_strategy"] = "once"
        
        elif page_type == "dashboard":
            strategy["wait_after_navigation"] = 2.0  # Dashboards load slowly
            strategy["wait_between_actions"] = 0.5
            strategy["screenshot_frequency"] = "after_important"
            strategy["selector_strategy"] = "conservative"  # Dashboards are stable
            strategy["retry_strategy"] = "once"
        
        elif page_type == "search":
            strategy["wait_after_navigation"] = 1.5
            strategy["wait_between_actions"] = 0.5
            strategy["screenshot_frequency"] = "after_important"
            strategy["selector_strategy"] = "balanced"
            strategy["retry_strategy"] = "once"
        
        elif page_type == "calendar":
            strategy["wait_after_navigation"] = 2.0  # Calendar views load slowly
            strategy["wait_between_actions"] = 1.0  # Calendar interactions need time
            strategy["screenshot_frequency"] = "always"  # Calendar state is important
            strategy["selector_strategy"] = "aggressive"  # Calendar elements vary
            strategy["retry_strategy"] = "multiple"
        
        # Adapt based on action context
        if action_context == "click":
            strategy["wait_between_actions"] = 1.0  # Clicks need more time
        elif action_context == "type":
            strategy["wait_between_actions"] = 0.3  # Typing is fast
        elif action_context == "submit":
            strategy["wait_after_navigation"] = 2.0  # Submissions cause redirects
            strategy["screenshot_frequency"] = "always"  # Capture submission result
        
        return strategy
    
    def get_optimal_wait_time(
        self,
        action_type: str,
        context: Dict[str, Any],
        strategy: Dict[str, Any]
    ) -> float:
        """Get optimal wait time based on context and strategy"""
        base_waits = {
            "NavigateAction": strategy.get("wait_after_navigation", 1.5),
            "ClickAction": strategy.get("wait_between_actions", 0.5),
            "TypeAction": strategy.get("wait_between_actions", 0.3),
            "WaitAction": 0.0,
            "ScreenshotAction": 0.1,
        }
        
        wait = base_waits.get(action_type, 0.5)
        
        # Adjust based on page type
        if context.get("is_login_page"):
            if action_type == "ClickAction":
                wait = max(wait, 1.0)  # Login clicks need more time
        elif context.get("is_calendar_page"):
            if action_type == "ClickAction":
                wait = max(wait, 1.5)  # Calendar clicks need more time
        
        return wait
    
    def should_take_screenshot(
        self,
        action_type: str,
        action_index: int,
        total_actions: int,
        strategy: Dict[str, Any]
    ) -> bool:
        """Determine if screenshot should be taken after this action"""
        frequency = strategy.get("screenshot_frequency", "after_important")
        
        if frequency == "always":
            return True
        elif frequency == "minimal":
            return action_index == total_actions - 1  # Only at the end
        elif frequency == "after_important":
            # Screenshot after important actions
            important_actions = ["NavigateAction", "ClickAction", "TypeAction"]
            if action_type in important_actions:
                # Screenshot after navigation, important clicks, and form submissions
                if action_type == "NavigateAction":
                    return True
                elif action_type == "ClickAction":
                    # Screenshot after clicks that might change state
                    return True
                elif action_type == "TypeAction":
                    # Screenshot after typing in forms (but not every keystroke)
                    return action_index % 2 == 0  # Every other type action
            return False
        
        return False
    
    def track_context(self, context: Dict[str, Any]):
        """Track context for multi-step flows"""
        self.context_history.append(context)
        # Keep only last 10 contexts
        if len(self.context_history) > 10:
            self.context_history.pop(0)
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get context history for multi-step flows"""
        return self.context_history.copy()


# Global instance
context_aware = ContextAwareAgent()

