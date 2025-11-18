"""
Task Diversity Handler - Dynamic Zero Compliance
Ensures miner handles task variations and doesn't overfit
"""
from typing import Dict, Any, List, Optional
import re
from collections import defaultdict
from datetime import datetime, timedelta


class TaskDiversityHandler:
    """
    Promotes task diversity and prevents overfitting by:
    1. Detecting task variations
    2. Adapting actions to variations
    3. Tracking task type distribution
    4. Ensuring balanced task handling
    """
    
    def __init__(self):
        self.task_type_counts = defaultdict(int)
        self.website_counts = defaultdict(int)
        self.recent_task_types = []
        self.variation_patterns = defaultdict(list)
    
    def analyze_task_diversity(self, prompt: str, url: str) -> Dict[str, Any]:
        """Analyze task for diversity and variation"""
        task_type = self._detect_task_type(prompt)
        website = self._extract_website(url)
        
        # Track distribution
        self.task_type_counts[task_type] += 1
        self.website_counts[website] += 1
        
        self.recent_task_types.append({
            "type": task_type,
            "website": website,
            "timestamp": datetime.now()
        })
        
        # Keep only last 100
        if len(self.recent_task_types) > 100:
            self.recent_task_types.pop(0)
        
        # Check for diversity issues
        diversity_issues = []
        
        # Check if one task type dominates
        if len(self.recent_task_types) > 20:
            type_distribution = defaultdict(int)
            for task in self.recent_task_types[-20:]:
                type_distribution[task["type"]] += 1
            
            max_type_ratio = max(type_distribution.values()) / len(self.recent_task_types[-20:])
            if max_type_ratio > 0.7:  # One type > 70%
                diversity_issues.append(f"Task type imbalance: {max(type_distribution.items(), key=lambda x: x[1])[0]} dominates")
        
        # Check if one website dominates
        if len(self.recent_task_types) > 20:
            website_distribution = defaultdict(int)
            for task in self.recent_task_types[-20:]:
                website_distribution[task["website"]] += 1
            
            max_website_ratio = max(website_distribution.values()) / len(self.recent_task_types[-20:])
            if max_website_ratio > 0.7:  # One website > 70%
                diversity_issues.append(f"Website imbalance: {max(website_distribution.items(), key=lambda x: x[1])[0]} dominates")
        
        return {
            "task_type": task_type,
            "website": website,
            "diversity_issues": diversity_issues,
            "type_distribution": dict(type_distribution) if len(self.recent_task_types) > 20 else {},
            "website_distribution": dict(website_distribution) if len(self.recent_task_types) > 20 else {}
        }
    
    def _detect_task_type(self, prompt: str) -> str:
        """Detect task type from prompt"""
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ["login", "sign in", "authenticate"]):
            return "login"
        elif any(kw in prompt_lower for kw in ["form", "fill", "submit"]):
            return "form"
        elif any(kw in prompt_lower for kw in ["click", "select", "choose"]):
            return "click"
        elif any(kw in prompt_lower for kw in ["search", "find", "look for"]):
            return "search"
        elif any(kw in prompt_lower for kw in ["book", "reserve", "schedule"]):
            return "booking"
        elif any(kw in prompt_lower for kw in ["upload", "file", "attach"]):
            return "upload"
        elif any(kw in prompt_lower for kw in ["calendar", "date", "month"]):
            return "calendar"
        else:
            return "generic"
    
    def _extract_website(self, url: str) -> str:
        """Extract website from URL"""
        if not url:
            return "unknown"
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Extract site name
            if "autocalendar" in domain:
                return "autocalendar"
            elif "autocinema" in domain:
                return "autocinema"
            elif "autodelivery" in domain:
                return "autodelivery"
            elif "autozone" in domain:
                return "autozone"
            elif "autowork" in domain:
                return "autowork"
            elif "autolist" in domain:
                return "autolist"
            elif "autobooks" in domain:
                return "autobooks"
            elif "autocrm" in domain:
                return "autocrm"
            elif "autodrive" in domain:
                return "autodrive"
            elif "automail" in domain:
                return "automail"
            elif "autodining" in domain:
                return "autodining"
            elif "autoconnect" in domain:
                return "autoconnect"
            elif "autolodge" in domain:
                return "autolodge"
            else:
                return domain.split('.')[0] if '.' in domain else domain
        except:
            return "unknown"
    
    def adapt_actions_for_variation(
        self,
        actions: List[Dict[str, Any]],
        task_variation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Adapt actions to handle task variations"""
        # Add variation markers to actions
        adapted_actions = []
        
        for action in actions:
            adapted_action = action.copy()
            
            # Add variation handling
            if "selector" in adapted_action:
                # Make selector more flexible for variations
                selector = adapted_action["selector"]
                
                # If selector is too specific, add alternatives
                if selector.startswith("#") or selector.startswith("."):
                    # Add data attribute fallback
                    adapted_action["selector_fallback"] = f"[data-testid='{selector[1:]}']"
            
            adapted_actions.append(adapted_action)
        
        return adapted_actions
    
    def get_diversity_metrics(self) -> Dict[str, Any]:
        """Get diversity metrics"""
        return {
            "task_type_distribution": dict(self.task_type_counts),
            "website_distribution": dict(self.website_counts),
            "recent_tasks_count": len(self.recent_task_types),
            "unique_task_types": len(set(t["type"] for t in self.recent_task_types)),
            "unique_websites": len(set(t["website"] for t in self.recent_task_types))
        }


# Global instance
task_diversity = TaskDiversityHandler()

