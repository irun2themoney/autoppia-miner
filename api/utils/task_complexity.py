"""Task complexity detection for smart agent routing"""
from typing import Dict, Any
import re


class TaskComplexityAnalyzer:
    """Analyze task complexity to determine best agent strategy"""
    
    SIMPLE_PATTERNS = [
        r"\b(click|select|choose|pick)\b",
        r"\b(view|show|display)\b",
        r"\b(navigate|go to|open)\b",
    ]
    
    COMPLEX_PATTERNS = [
        r"\b(login|sign in|authenticate)\b",
        r"\b(form|fill|submit|enter)\b",
        r"\b(modify|edit|change|update|delete)\b",
        r"\b(search|find|look for)\b",
        r"\b(comment|post|reply)\b",
        r"\b(multiple|several|many)\b",
        r"\b(and|then|after|before)\b",  # Multi-step indicators
    ]
    
    def analyze(self, prompt: str, url: str = "") -> Dict[str, Any]:
        """Analyze task complexity"""
        prompt_lower = prompt.lower()
        
        # Count complexity indicators
        simple_count = sum(1 for pattern in self.SIMPLE_PATTERNS if re.search(pattern, prompt_lower))
        complex_count = sum(1 for pattern in self.COMPLEX_PATTERNS if re.search(pattern, prompt_lower))
        
        # Count action words (more actions = more complex)
        action_words = ["click", "type", "fill", "submit", "navigate", "search", "modify", "edit"]
        action_count = sum(1 for word in action_words if word in prompt_lower)
        
        # Check for multi-step indicators
        has_multiple_steps = any(word in prompt_lower for word in ["and", "then", "after", "before", "first", "next"])
        
        # Determine complexity
        if complex_count >= 2 or action_count >= 3 or has_multiple_steps:
            complexity = "high"
        elif complex_count >= 1 or action_count >= 2:
            complexity = "medium"
        else:
            complexity = "low"
        
        # Estimate required intelligence
        requires_llm = complexity in ["medium", "high"]
        
        return {
            "complexity": complexity,
            "simple_indicators": simple_count,
            "complex_indicators": complex_count,
            "action_count": action_count,
            "has_multiple_steps": has_multiple_steps,
            "requires_llm": requires_llm,
            "estimated_actions": max(3, action_count * 2),  # Rough estimate
        }

