"""Validator Behavior Learning - Learn what validators reward and optimize for it"""
from typing import Dict, Any, List, Optional
from collections import defaultdict
import logging
import time

logger = logging.getLogger(__name__)


class ValidatorLearner:
    """
    Learn validator behavior and preferences
    Tracks which actions get highest scores and optimizes for specific validators
    """
    
    def __init__(self):
        # Validator-specific data
        self.validator_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Action success tracking
        self.action_success_rates: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(lambda: {"success": 0, "total": 0}))
        
        # Task type success by validator
        self.task_type_success: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(lambda: {"success": 0, "total": 0}))
        
        # Selector success by validator
        self.selector_success: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(lambda: {"success": 0, "total": 0}))
        
        # Response time preferences
        self.response_time_preferences: Dict[str, List[float]] = defaultdict(list)
        
        # Learning history
        self.learning_history: List[Dict[str, Any]] = []
    
    def record_result(
        self,
        validator_ip: str,
        task_prompt: str,
        task_url: str,
        actions: List[Dict[str, Any]],
        success: bool,
        response_time: float,
        task_type: Optional[str] = None,
        score: Optional[float] = None
    ):
        """
        Record validator result for learning
        
        Args:
            validator_ip: Validator IP address
            task_prompt: Task prompt
            task_url: Task URL
            actions: Action sequence that was executed
            success: Whether task succeeded
            response_time: Response time in seconds
            task_type: Type of task (login, form, click, etc.)
            score: Validator score (if available)
        """
        if not validator_ip or validator_ip in ["localhost", "127.0.0.1", "::1"]:
            return  # Skip local tests
        
        # Update validator patterns
        if validator_ip not in self.validator_patterns:
            self.validator_patterns[validator_ip] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "preferred_task_types": {},
                "preferred_selectors": {},
                "last_seen": time.time()
            }
        
        validator_data = self.validator_patterns[validator_ip]
        validator_data["total_requests"] += 1
        validator_data["last_seen"] = time.time()
        
        if success:
            validator_data["successful_requests"] += 1
        else:
            validator_data["failed_requests"] += 1
        
        # Update average response time
        current_avg = validator_data["avg_response_time"]
        total = validator_data["total_requests"]
        validator_data["avg_response_time"] = (current_avg * (total - 1) + response_time) / total
        
        # Track task type success
        if task_type:
            task_data = self.task_type_success[validator_ip][task_type]
            task_data["total"] += 1
            if success:
                task_data["success"] += 1
        
        # Track action success
        for action in actions:
            action_type = action.get("action_type") or action.get("type", "")
            if action_type:
                action_data = self.action_success_rates[validator_ip][action_type]
                action_data["total"] += 1
                if success:
                    action_data["success"] += 1
            
            # Track selector success
            selector = action.get("selector")
            if selector:
                selector_type = selector.get("type", "") if isinstance(selector, dict) else "unknown"
                if selector_type:
                    selector_data = self.selector_success[validator_ip][selector_type]
                    selector_data["total"] += 1
                    if success:
                        selector_data["success"] += 1
        
        # Track response time preferences (successful requests)
        if success:
            self.response_time_preferences[validator_ip].append(response_time)
            # Keep only last 100 response times
            if len(self.response_time_preferences[validator_ip]) > 100:
                self.response_time_preferences[validator_ip].pop(0)
        
        # Record in learning history
        self.learning_history.append({
            "validator_ip": validator_ip,
            "task_prompt": task_prompt[:100],  # First 100 chars
            "task_url": task_url,
            "task_type": task_type,
            "success": success,
            "response_time": response_time,
            "score": score,
            "action_count": len(actions),
            "timestamp": time.time()
        })
        
        # Keep only last 1000 learning records
        if len(self.learning_history) > 1000:
            self.learning_history.pop(0)
        
        logger.info(f"Validator learner: Recorded result for {validator_ip} - Success: {success}, Response: {response_time:.2f}s")
    
    def get_validator_preferences(
        self,
        validator_ip: str
    ) -> Dict[str, Any]:
        """
        Get preferences for a specific validator
        
        Returns:
            Dictionary with validator preferences
        """
        if validator_ip not in self.validator_patterns:
            return {}
        
        validator_data = self.validator_patterns[validator_ip]
        
        # Calculate success rates
        total = validator_data["total_requests"]
        success_rate = (validator_data["successful_requests"] / total * 100) if total > 0 else 0.0
        
        # Get preferred task types
        preferred_task_types = {}
        for task_type, data in self.task_type_success[validator_ip].items():
            if data["total"] > 0:
                preferred_task_types[task_type] = {
                    "success_rate": (data["success"] / data["total"] * 100),
                    "total": data["total"]
                }
        
        # Get preferred selectors
        preferred_selectors = {}
        for selector_type, data in self.selector_success[validator_ip].items():
            if data["total"] > 0:
                preferred_selectors[selector_type] = {
                    "success_rate": (data["success"] / data["total"] * 100),
                    "total": data["total"]
                }
        
        # Get preferred response time
        response_times = self.response_time_preferences[validator_ip]
        preferred_response_time = sum(response_times) / len(response_times) if response_times else None
        
        return {
            "validator_ip": validator_ip,
            "total_requests": total,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(validator_data["avg_response_time"], 2),
            "preferred_response_time": round(preferred_response_time, 2) if preferred_response_time else None,
            "preferred_task_types": preferred_task_types,
            "preferred_selectors": preferred_selectors,
            "last_seen": validator_data["last_seen"]
        }
    
    def get_optimal_strategy(
        self,
        validator_ip: str,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get optimal strategy for a validator based on learned patterns
        
        Returns:
            Dictionary with optimal strategy parameters
        """
        preferences = self.get_validator_preferences(validator_ip)
        
        if not preferences:
            return {}  # No data for this validator
        
        strategy = {
            "target_response_time": preferences.get("preferred_response_time") or 2.0,
            "use_verification": True,  # Default
            "wait_times": {
                "navigation": 2.0,
                "click": 1.0,
                "type": 0.5,
                "submit": 2.0
            }
        }
        
        # Adjust based on validator preferences
        if task_type and task_type in preferences.get("preferred_task_types", {}):
            task_data = preferences["preferred_task_types"][task_type]
            if task_data["success_rate"] > 80:
                # This validator likes this task type, use standard strategy
                pass
            elif task_data["success_rate"] < 50:
                # This validator is strict, add more verification
                strategy["use_verification"] = True
                strategy["wait_times"]["navigation"] += 0.5
                strategy["wait_times"]["click"] += 0.3
        
        # Adjust response time based on validator preference
        preferred_rt = preferences.get("preferred_response_time")
        if preferred_rt:
            if preferred_rt < 1.0:
                # Validator prefers fast responses
                strategy["target_response_time"] = 1.0
            elif preferred_rt > 5.0:
                # Validator prefers slower, more careful responses
                strategy["target_response_time"] = 5.0
                strategy["wait_times"]["navigation"] += 1.0
                strategy["wait_times"]["click"] += 0.5
        
        return strategy
    
    def get_all_validator_stats(self) -> Dict[str, Any]:
        """Get statistics for all validators"""
        return {
            "total_validators": len(self.validator_patterns),
            "validators": {
                ip: self.get_validator_preferences(ip)
                for ip in self.validator_patterns.keys()
            },
            "total_learning_records": len(self.learning_history)
        }
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning data"""
        if not self.learning_history:
            return {"insights": "No learning data yet"}
        
        # Calculate overall success rate
        total = len(self.learning_history)
        successful = sum(1 for r in self.learning_history if r["success"])
        overall_success_rate = (successful / total * 100) if total > 0 else 0.0
        
        # Find most successful task types
        task_type_success = defaultdict(lambda: {"success": 0, "total": 0})
        for record in self.learning_history:
            task_type = record.get("task_type", "unknown")
            task_type_success[task_type]["total"] += 1
            if record["success"]:
                task_type_success[task_type]["success"] += 1
        
        best_task_types = {}
        for task_type, data in task_type_success.items():
            if data["total"] > 0:
                success_rate = (data["success"] / data["total"] * 100)
                if data["total"] >= 3:  # At least 3 samples
                    best_task_types[task_type] = {
                        "success_rate": round(success_rate, 2),
                        "total": data["total"]
                    }
        
        # Sort by success rate
        best_task_types = dict(sorted(
            best_task_types.items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )[:5])  # Top 5
        
        return {
            "overall_success_rate": round(overall_success_rate, 2),
            "total_records": total,
            "best_task_types": best_task_types,
            "total_validators": len(self.validator_patterns)
        }


# Global instance
validator_learner = ValidatorLearner()

