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
        """Extract credentials from prompt"""
        prompt_lower = prompt.lower()
        credentials = {}
        
        for cred_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    # Clean up common placeholders
                    value = value.replace("<web_agent_id>", "").strip()
                    if value:
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
        """Extract target element description"""
        # Common patterns
        patterns = [
            r"click (?:the |a )?([^,\.]+?)(?: button|link|element)?",
            r"select (?:the |a )?([^,\.]+?)(?: button|link|element)?",
            r"choose (?:the |a )?([^,\.]+?)(?: button|link|element)?",
            r"find (?:the |a )?([^,\.]+?)(?: button|link|element)?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                target = match.group(1).strip()
                # Remove common words
                target = re.sub(r"\b(the|a|an|on|in|at)\b", "", target).strip()
                if target:
                    return target
        
        return None
    
    def parse_task(self, prompt: str, url: str = "") -> Dict[str, Any]:
        """Parse task and extract all relevant information"""
        parsed = {
            "original_prompt": prompt,
            "url": self.extract_url(prompt, url),
            "credentials": self.extract_credentials(prompt),
            "text_to_type": self.extract_text_to_type(prompt),
            "target_element": self.extract_target_element(prompt),
            "has_login": any(word in prompt.lower() for word in ["login", "sign in", "log in"]),
            "has_form": any(word in prompt.lower() for word in ["form", "fill", "submit", "enter"]),
            "has_search": any(word in prompt.lower() for word in ["search", "find", "look for"]),
            "has_modify": any(word in prompt.lower() for word in ["modify", "edit", "change", "update"]),
        }
        
        return parsed

