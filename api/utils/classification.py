"""Task classification utilities"""
import re
from typing import Dict


class TaskClassifier:
    """Classify tasks based on prompt patterns"""
    
    PATTERNS = {
        "click": [
            r"\b(click|select|choose|pick|press|tap|switch|toggle|view|change|set)\b",
        ],
        "type": [
            r"\b(type|enter|fill|input|write|put)\b",
        ],
        "search": [
            r"\b(search|find|look|seek)\b",
        ],
        "form_fill": [
            r"\b(form|submit|login|sign|register)\b",
        ],
    }
    
    def classify(self, prompt: str) -> str:
        """Classify task type from prompt"""
        prompt_lower = prompt.lower()
        
        # Check patterns in order of specificity
        if any(re.search(pattern, prompt_lower) for pattern in self.PATTERNS["form_fill"]):
            return "form_fill"
        if any(re.search(pattern, prompt_lower) for pattern in self.PATTERNS["search"]):
            return "search"
        if any(re.search(pattern, prompt_lower) for pattern in self.PATTERNS["type"]):
            return "type"
        if any(re.search(pattern, prompt_lower) for pattern in self.PATTERNS["click"]):
            return "click"
        
        return "generic"

