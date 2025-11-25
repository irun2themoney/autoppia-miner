"""
Self-Learning and Self-Enhancing System for Autoppia Miner

This module implements a learning system that:
1. Tracks action success/failure rates
2. Learns from selector effectiveness
3. Adapts to different task types
4. Improves action sequences over time
5. Optimizes based on validator feedback
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)

# Learning data storage
LEARNING_DATA_FILE = "learning_data.pkl"
SELECTOR_SUCCESS_FILE = "selector_success.json"
TASK_TYPE_PATTERNS_FILE = "task_patterns.json"


class LearningSystem:
    """
    Self-learning system that improves miner performance over time
    """
    
    def __init__(self):
        self.learning_data = self._load_learning_data()
        self.selector_success = self._load_selector_success()
        self.task_patterns = self._load_task_patterns()
        
        # Statistics
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "selector_attempts": defaultdict(int),
            "selector_successes": defaultdict(int),
            "action_type_usage": defaultdict(int),
            "task_type_patterns": defaultdict(list),
        }
        
        logger.info("🧠 Learning System initialized")
    
    def _load_learning_data(self) -> Dict[str, Any]:
        """Load learning data from disk"""
        if os.path.exists(LEARNING_DATA_FILE):
            try:
                with open(LEARNING_DATA_FILE, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load learning data: {e}")
        return {
            "successful_actions": [],
            "failed_actions": [],
            "selector_effectiveness": {},
            "task_type_success": {},
        }
    
    def _load_selector_success(self) -> Dict[str, float]:
        """Load selector success rates"""
        if os.path.exists(SELECTOR_SUCCESS_FILE):
            try:
                with open(SELECTOR_SUCCESS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load selector success: {e}")
        return {}
    
    def _load_task_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load successful task patterns"""
        if os.path.exists(TASK_TYPE_PATTERNS_FILE):
            try:
                with open(TASK_TYPE_PATTERNS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load task patterns: {e}")
        return {}
    
    def _save_learning_data(self):
        """Save learning data to disk"""
        try:
            with open(LEARNING_DATA_FILE, 'wb') as f:
                pickle.dump(self.learning_data, f)
        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")
    
    def _save_selector_success(self):
        """Save selector success rates"""
        try:
            with open(SELECTOR_SUCCESS_FILE, 'w') as f:
                json.dump(self.selector_success, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save selector success: {e}")
    
    def _save_task_patterns(self):
        """Save task patterns"""
        try:
            with open(TASK_TYPE_PATTERNS_FILE, 'w') as f:
                json.dump(self.task_patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task patterns: {e}")
    
    def record_task_result(
        self,
        task_id: str,
        task_type: str,
        prompt: str,
        url: str,
        actions: List[Dict[str, Any]],
        success: bool,
        execution_time: float,
        error: Optional[str] = None
    ):
        """
        Record task execution result for learning
        
        Args:
            task_id: Unique task identifier
            task_type: Type of task (login, form, search, etc.)
            prompt: Task prompt
            url: Target URL
            actions: Actions that were executed
            success: Whether task succeeded
            execution_time: Time taken to execute
            error: Error message if failed
        """
        self.stats["total_tasks"] += 1
        
        if success:
            self.stats["successful_tasks"] += 1
            
            # Record successful pattern
            if task_type not in self.task_patterns:
                self.task_patterns[task_type] = []
            
            pattern = {
                "prompt": prompt[:200],  # Truncate for storage
                "url": url,
                "actions": actions,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }
            
            self.task_patterns[task_type].append(pattern)
            
            # Keep only last 100 successful patterns per task type
            if len(self.task_patterns[task_type]) > 100:
                self.task_patterns[task_type] = self.task_patterns[task_type][-100:]
            
            # Record successful selectors
            for action in actions:
                if "selector" in action and isinstance(action["selector"], dict):
                    selector_key = self._get_selector_key(action["selector"])
                    self.stats["selector_attempts"][selector_key] += 1
                    self.stats["selector_successes"][selector_key] += 1
                
                # Track action type usage
                action_type = action.get("type", "Unknown")
                self.stats["action_type_usage"][action_type] += 1
        else:
            self.stats["failed_tasks"] += 1
            
            # Record failed selectors
            for action in actions:
                if "selector" in action and isinstance(action["selector"], dict):
                    selector_key = self._get_selector_key(action["selector"])
                    self.stats["selector_attempts"][selector_key] += 1
                    # Don't increment success for failed tasks
        
        # Update selector success rates
        self._update_selector_success_rates()
        
        # Save periodically (every 10 tasks)
        if self.stats["total_tasks"] % 10 == 0:
            self._save_learning_data()
            self._save_selector_success()
            self._save_task_patterns()
            logger.info(f"💾 Learning data saved: {self.stats['total_tasks']} tasks processed")
    
    def _get_selector_key(self, selector: Dict[str, Any]) -> str:
        """Generate a key for selector tracking"""
        selector_type = selector.get("type", "unknown")
        value = selector.get("value", "")
        attribute = selector.get("attribute", "")
        
        if selector_type == "attributeValueSelector":
            return f"{selector_type}:{attribute}:{value[:50]}"
        else:
            return f"{selector_type}:{value[:50]}"
    
    def _update_selector_success_rates(self):
        """Update selector success rates based on statistics"""
        for selector_key, attempts in self.stats["selector_attempts"].items():
            successes = self.stats["selector_successes"].get(selector_key, 0)
            if attempts > 0:
                success_rate = successes / attempts
                self.selector_success[selector_key] = success_rate
    
    def get_best_selectors(self, element_type: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get best performing selectors for a given element type
        
        Args:
            element_type: Type of element (button, input, link, etc.)
            limit: Maximum number of selectors to return
            
        Returns:
            List of (selector_key, success_rate) tuples, sorted by success rate
        """
        # Filter selectors by element type (simplified - could be enhanced)
        relevant_selectors = [
            (key, rate) for key, rate in self.selector_success.items()
            if element_type.lower() in key.lower() or element_type.lower() == "any"
        ]
        
        # Sort by success rate (descending)
        relevant_selectors.sort(key=lambda x: x[1], reverse=True)
        
        return relevant_selectors[:limit]
    
    def get_successful_pattern(self, task_type: str, prompt: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get a successful action pattern for a similar task
        
        Args:
            task_type: Type of task
            prompt: Task prompt
            
        Returns:
            Successful action pattern if found, None otherwise
        """
        if task_type not in self.task_patterns:
            return None
        
        # Find most similar successful pattern
        prompt_lower = prompt.lower()
        best_match = None
        best_score = 0
        
        for pattern in self.task_patterns[task_type]:
            pattern_prompt = pattern["prompt"].lower()
            
            # Simple similarity score (could be enhanced with NLP)
            common_words = set(prompt_lower.split()) & set(pattern_prompt.split())
            score = len(common_words) / max(len(prompt_lower.split()), 1)
            
            if score > best_score:
                best_score = score
                best_match = pattern
        
        if best_match and best_score > 0.3:  # Minimum similarity threshold
            logger.info(f"🎯 Found similar successful pattern (similarity: {best_score:.2f})")
            return best_match["actions"]
        
        return None
    
    def get_selector_success_rate(self, selector: Dict[str, Any]) -> float:
        """
        Get success rate for a specific selector
        
        Args:
            selector: Selector dictionary
            
        Returns:
            Success rate (0.0 to 1.0), or 0.5 if unknown (neutral)
        """
        selector_key = self._get_selector_key(selector)
        return self.selector_success.get(selector_key, 0.5)  # Default to neutral
    
    def should_use_selector(self, selector: Dict[str, Any], min_success_rate: float = 0.3) -> bool:
        """
        Determine if a selector should be used based on success rate
        
        Args:
            selector: Selector dictionary
            min_success_rate: Minimum success rate to use selector
            
        Returns:
            True if selector should be used, False otherwise
        """
        success_rate = self.get_selector_success_rate(selector)
        return success_rate >= min_success_rate
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        total = self.stats["total_tasks"]
        success_rate = (
            self.stats["successful_tasks"] / total
            if total > 0
            else 0.0
        )
        
        return {
            "total_tasks": total,
            "successful_tasks": self.stats["successful_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "success_rate": success_rate,
            "selector_tracked": len(self.selector_success),
            "task_patterns": len(self.task_patterns),
            "action_type_usage": dict(self.stats["action_type_usage"]),
        }
    
    def enhance_actions(
        self,
        actions: List[Dict[str, Any]],
        task_type: str,
        prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Enhance actions based on learned patterns
        
        Args:
            actions: Original actions
            task_type: Type of task
            prompt: Task prompt
            
        Returns:
            Enhanced actions
        """
        enhanced = actions.copy()
        
        # Try to find a successful pattern for this task type
        successful_pattern = self.get_successful_pattern(task_type, prompt)
        
        if successful_pattern:
            logger.info(f"✨ Enhancing actions using learned pattern for {task_type}")
            # Could merge or replace actions with successful pattern
            # For now, just log that we found a pattern
        
        # Enhance selectors based on success rates
        for i, action in enumerate(enhanced):
            if "selector" in action and isinstance(action["selector"], dict):
                selector = action["selector"]
                success_rate = self.get_selector_success_rate(selector)
                
                # If selector has low success rate, try to improve it
                if success_rate < 0.3:
                    logger.debug(f"⚠️ Selector has low success rate ({success_rate:.2f}), may need improvement")
                    # Could try alternative selectors here
        
        return enhanced


# Global learning system instance
_learning_system: Optional[LearningSystem] = None


def get_learning_system() -> LearningSystem:
    """Get or create global learning system instance"""
    global _learning_system
    if _learning_system is None:
        _learning_system = LearningSystem()
    return _learning_system

