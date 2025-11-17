"""Validator feedback loop for continuous improvement"""
from typing import Dict, Any, List, Optional
import json
import os
from collections import defaultdict
from datetime import datetime
import logging


class FeedbackLoop:
    """Learn from validator feedback to improve performance"""
    
    def __init__(self, feedback_file: str = "/tmp/autoppia_feedback.json"):
        self.feedback_file = feedback_file
        self.feedback_data: Dict[str, Any] = {
            "successful_patterns": defaultdict(int),
            "failed_patterns": defaultdict(int),
            "selector_success": defaultdict(int),
            "selector_failures": defaultdict(int),
            "action_success_rates": defaultdict(lambda: {"success": 0, "total": 0}),
            "last_updated": None,
        }
        self.load_feedback()
    
    def load_feedback(self):
        """Load feedback data from disk"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    data = json.load(f)
                    self.feedback_data.update(data)
            except Exception as e:
                logging.warning(f"Failed to load feedback: {e}")
    
    def save_feedback(self):
        """Save feedback data to disk"""
        try:
            self.feedback_data["last_updated"] = datetime.now().isoformat()
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save feedback: {e}")
    
    def record_success(self, task_id: str, prompt: str, url: str, actions: List[Dict[str, Any]], score: Optional[float] = None):
        """Record successful task completion"""
        pattern_key = self._get_pattern_key(prompt, url)
        self.feedback_data["successful_patterns"][pattern_key] += 1
        
        # Track selector success
        for action in actions:
            if action.get("type") == "ClickAction" and action.get("selector"):
                selector_key = self._get_selector_key(action["selector"])
                self.feedback_data["selector_success"][selector_key] += 1
        
        # Track action success rates
        for action in actions:
            action_type = action.get("type", "unknown")
            self.feedback_data["action_success_rates"][action_type]["success"] += 1
            self.feedback_data["action_success_rates"][action_type]["total"] += 1
        
        # Save periodically
        if self.feedback_data["successful_patterns"][pattern_key] % 10 == 0:
            self.save_feedback()
    
    def record_failure(self, task_id: str, prompt: str, url: str, actions: List[Dict[str, Any]], error: Optional[str] = None):
        """Record failed task completion"""
        pattern_key = self._get_pattern_key(prompt, url)
        self.feedback_data["failed_patterns"][pattern_key] += 1
        
        # Track selector failures
        for action in actions:
            if action.get("type") == "ClickAction" and action.get("selector"):
                selector_key = self._get_selector_key(action["selector"])
                self.feedback_data["selector_failures"][selector_key] += 1
        
        # Track action failure rates
        for action in actions:
            action_type = action.get("type", "unknown")
            self.feedback_data["action_success_rates"][action_type]["total"] += 1
        
        # Save periodically
        if self.feedback_data["failed_patterns"][pattern_key] % 10 == 0:
            self.save_feedback()
    
    def get_successful_pattern(self, prompt: str, url: str) -> Optional[List[Dict[str, Any]]]:
        """Get a successful pattern for similar task"""
        pattern_key = self._get_pattern_key(prompt, url)
        
        # Check if we have a successful pattern
        success_count = self.feedback_data["successful_patterns"].get(pattern_key, 0)
        failure_count = self.feedback_data["failed_patterns"].get(pattern_key, 0)
        
        if success_count > failure_count and success_count >= 3:
            # This pattern has been successful, return confidence
            return {
                "confidence": success_count / (success_count + failure_count + 1),
                "success_count": success_count,
            }
        
        return None
    
    def get_best_selector_strategy(self, element_type: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get best selector strategy based on historical success"""
        # Analyze selector success rates
        best_selectors = []
        
        # Sort selectors by success rate
        selector_rates = {}
        for selector_key, success_count in self.feedback_data["selector_success"].items():
            failure_count = self.feedback_data["selector_failures"].get(selector_key, 0)
            total = success_count + failure_count
            if total > 0:
                selector_rates[selector_key] = success_count / total
        
        # Return top performing selectors
        sorted_selectors = sorted(selector_rates.items(), key=lambda x: x[1], reverse=True)
        for selector_key, rate in sorted_selectors[:5]:
            if rate > 0.5:  # Only use selectors with >50% success rate
                try:
                    selector = json.loads(selector_key)
                    best_selectors.append(selector)
                except:
                    pass
        
        return best_selectors
    
    def get_action_success_rate(self, action_type: str) -> float:
        """Get success rate for specific action type"""
        stats = self.feedback_data["action_success_rates"].get(action_type, {"success": 0, "total": 0})
        if stats["total"] > 0:
            return stats["success"] / stats["total"]
        return 0.5  # Default 50% if no data
    
    def _get_pattern_key(self, prompt: str, url: str) -> str:
        """Generate pattern key"""
        import re
        normalized = prompt.lower()
        normalized = re.sub(r'username[:\s]+[^\s]+', 'username:XXX', normalized)
        normalized = re.sub(r'password[:\s]+[^\s]+', 'password:XXX', normalized)
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
        except:
            domain = ""
        
        return f"{normalized}|{domain}"
    
    def _get_selector_key(self, selector: Dict[str, Any]) -> str:
        """Generate selector key for tracking"""
        return json.dumps(selector, sort_keys=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        total_success = sum(self.feedback_data["successful_patterns"].values())
        total_failures = sum(self.feedback_data["failed_patterns"].values())
        total_tasks = total_success + total_failures
        
        return {
            "total_tasks": total_tasks,
            "success_count": total_success,
            "failure_count": total_failures,
            "success_rate": total_success / total_tasks if total_tasks > 0 else 0,
            "unique_patterns": len(self.feedback_data["successful_patterns"]),
            "action_success_rates": {
                action_type: stats["success"] / stats["total"] if stats["total"] > 0 else 0
                for action_type, stats in self.feedback_data["action_success_rates"].items()
            },
        }

