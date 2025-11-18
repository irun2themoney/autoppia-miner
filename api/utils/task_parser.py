"""Advanced task parsing and extraction"""
import re
from typing import Dict, Any, Optional, List


class TaskParser:
    """Parse and extract information from task prompts"""
    
    def __init__(self):
        # Common patterns for extraction
        self.credential_patterns = {
            "username": [
                r"username[:\s]+([^\s<]+)",
                r"user[:\s]+([^\s<]+)",
                r"login[:\s]+([^\s<]+)",
            ],
            "password": [
                r"password[:\s]+([^\s<]+)",
                r"pass[:\s]+([^\s<]+)",
            ],
            "email": [
                r"email[:\s]+([^\s@]+@[^\s@]+\.[^\s@]+)",
                r"e-mail[:\s]+([^\s@]+@[^\s@]+\.[^\s@]+)",
            ],
        }
        
        self.url_patterns = [
            r"https?://[^\s]+",
            r"www\.[^\s]+",
            r"navigate to ([^\s]+)",
            r"go to ([^\s]+)",
        ]
        
        self.text_patterns = [
            r"type ['\"]([^'\"]+)['\"]",
            r"enter ['\"]([^'\"]+)['\"]",
            r"fill with ['\"]([^'\"]+)['\"]",
            r"contains the word ['\"]([^'\"]+)['\"]",
            r"contains ['\"]([^'\"]+)['\"]",
        ]
    
    def extract_credentials(self, prompt: str) -> Dict[str, Optional[str]]:
        """Extract credentials from prompt - Enhanced with more patterns"""
        prompt_lower = prompt.lower()
        credentials = {}
        
        # Enhanced patterns for better extraction
        enhanced_patterns = {
            "username": [
                r"username[:\s=]+([^\s<,]+)",
                r"user[:\s=]+([^\s<,]+)",
                r"login[:\s=]+([^\s<,]+)",
                r"user\s+name[:\s=]+([^\s<,]+)",
                r"uname[:\s=]+([^\s<,]+)",
            ],
            "password": [
                r"password[:\s=]+([^\s<,]+)",
                r"pass[:\s=]+([^\s<,]+)",
                r"pwd[:\s=]+([^\s<,]+)",
            ],
            "email": [
                r"email[:\s=]+([^\s<,]+@[^\s<,]+)",
                r"e-mail[:\s=]+([^\s<,]+@[^\s<,]+)",
                r"mail[:\s=]+([^\s<,]+@[^\s<,]+)",
            ],
        }
        
        for cred_type, patterns in enhanced_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    # Clean up common placeholders and separators
                    value = value.replace("<web_agent_id>", "").strip()
                    value = value.rstrip(".,;:!?")  # Remove trailing punctuation
                    if value and len(value) > 0:
                        credentials[cred_type] = value
                        break
        
        return credentials
    
    def extract_url(self, prompt: str, default_url: str = "") -> str:
        """Extract URL from prompt"""
        for pattern in self.url_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                url = match.group(1) if match.groups() else match.group(0)
                # Ensure protocol
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                return url
        
        return default_url
    
    def extract_text_to_type(self, prompt: str) -> Optional[str]:
        """Extract text that needs to be typed"""
        for pattern in self.text_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_target_element(self, prompt: str) -> Optional[str]:
        """Extract target element description - Enhanced patterns"""
        prompt_lower = prompt.lower()
        
        # Enhanced patterns for better extraction
        patterns = [
            r"click (?:the |a |on )?([^,\.]+?)(?: button|link|element|tab|option)?",
            r"select (?:the |a )?([^,\.]+?)(?: button|link|element|option|view)?",
            r"choose (?:the |a )?([^,\.]+?)(?: button|link|element|option)?",
            r"find (?:the |a )?([^,\.]+?)(?: button|link|element)?",
            r"switch (?:to |the )?([^,\.]+?)(?: view|mode|tab)?",
            r"toggle (?:the |to )?([^,\.]+?)(?: view|mode)?",
            r"view (?:the |a )?([^,\.]+?)(?: view|mode)?",
            r"change (?:to |the )?([^,\.]+?)(?: view|mode)?",
            r"open (?:the |a )?([^,\.]+?)(?: button|link|tab)?",
            r"press (?:the |a )?([^,\.]+?)(?: button|key)?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                target = match.group(1).strip()
                # Remove common words
                target = re.sub(r"\b(the|a|an|on|in|at|to|for|with|from)\b", "", target).strip()
                if target and len(target) > 1:
                    return target
        
        # Try to extract from common phrases
        common_targets = {
            "month view": "month",
            "week view": "week",
            "day view": "day",
            "year view": "year",
            "login button": "login",
            "submit button": "submit",
            "search button": "search",
            "profile": "profile",
            "settings": "settings",
        }
        
        for phrase, target in common_targets.items():
            if phrase in prompt_lower:
                return target
        
        return None
    
    def parse_task(self, prompt: str, url: str = "") -> Dict[str, Any]:
        """Parse task and extract all relevant information - Enhanced"""
        prompt_lower = prompt.lower()
        
        # Enhanced task type detection
        has_login = any(word in prompt_lower for word in ["login", "sign in", "log in", "authenticate"])
        has_form = any(word in prompt_lower for word in ["form", "fill", "submit", "enter", "register"])
        has_search = any(word in prompt_lower for word in ["search", "find", "look for", "seek"])
        has_modify = any(word in prompt_lower for word in ["modify", "edit", "change", "update", "delete", "remove"])
        has_click = any(word in prompt_lower for word in ["click", "select", "choose", "switch", "toggle", "view"])
        has_type = any(word in prompt_lower for word in ["type", "enter", "input", "write"])
        has_comment = any(word in prompt_lower for word in ["comment", "post", "reply", "write a comment"])
        has_scroll = any(word in prompt_lower for word in ["scroll", "move down", "move up"])
        has_extract = any(word in prompt_lower for word in ["extract", "get", "read", "retrieve", "fetch"])
        has_multistep = any(word in prompt_lower for word in ["and", "then", "after", "before", "first", "next"])
        
        # Determine task type with priority
        if has_login:
            task_type = "login"
        elif has_form:
            task_type = "form"
        elif has_modify:
            task_type = "modify"
        elif has_search:
            task_type = "search"
        elif has_comment:
            task_type = "comment"
        elif has_click:
            task_type = "click"
        elif has_type:
            task_type = "type"
        elif has_scroll:
            task_type = "scroll"
        elif has_extract:
            task_type = "extract"
        elif has_multistep:
            task_type = "multistep"
        else:
            task_type = "generic"
        
        parsed = {
            "original_prompt": prompt,
            "url": self.extract_url(prompt, url),
            "credentials": self.extract_credentials(prompt),
            "text_to_type": self.extract_text_to_type(prompt),
            "target_element": self.extract_target_element(prompt),
            "has_login": has_login,
            "has_form": has_form,
            "has_search": has_search,
            "has_modify": has_modify,
            "has_click": has_click,
            "has_type": has_type,
            "has_comment": has_comment,
            "has_scroll": has_scroll,
            "has_extract": has_extract,
            "has_multistep": has_multistep,
            "task_type": task_type,
        }
        
        return parsed

