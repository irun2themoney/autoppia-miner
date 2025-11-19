"""Action sequence optimization - remove redundant actions and optimize flow"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ActionOptimizer:
    """
    Optimize action sequences by removing redundant actions and improving flow
    Tok-style: Clean, efficient action sequences without redundancy
    """
    
    def __init__(self):
        self.optimization_history = []  # Track optimization results
    
    def optimize_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize action sequence by removing redundant actions
        
        Tok-style: Remove redundant waits, duplicate screenshots, unnecessary actions
        """
        if not actions:
            return actions
        
        optimized = []
        prev_action = None
        
        for i, action in enumerate(actions):
            action_type = action.get("action_type", "")
            
            # Skip redundant actions
            if self._is_redundant(action, prev_action, optimized):
                continue
            
            # Merge consecutive waits
            if action_type == "wait" and prev_action and prev_action.get("action_type") == "wait":
                # Merge waits (add durations)
                prev_duration = prev_action.get("duration", 0)
                curr_duration = action.get("duration", 0)
                optimized[-1]["duration"] = prev_duration + curr_duration
                prev_action = optimized[-1]
                continue
            
            # Remove duplicate screenshots (keep only last one before important action)
            if action_type == "screenshot":
                # Check if next action is important
                next_action = actions[i + 1] if i + 1 < len(actions) else None
                if next_action and next_action.get("action_type") in ["navigate", "click", "submit"]:
                    # Keep this screenshot (it's before important action)
                    optimized.append(action)
                    prev_action = action
                    continue
                elif prev_action and prev_action.get("action_type") == "screenshot":
                    # Skip duplicate screenshot
                    continue
            
            # Remove redundant navigation (if already on same URL)
            if action_type == "navigate":
                url = action.get("url", "")
                # Check if we already navigated to this URL
                if any(
                    a.get("action_type") == "navigate" and a.get("url") == url
                    for a in optimized
                ):
                    # Skip redundant navigation
                    continue
            
            # Remove redundant clicks (same selector, consecutive)
            if action_type == "click":
                selector = action.get("selector")
                if prev_action and prev_action.get("action_type") == "click":
                    prev_selector = prev_action.get("selector")
                    if self._selectors_equal(selector, prev_selector):
                        # Skip redundant click
                        continue
            
            # Add action
            optimized.append(action)
            prev_action = action
        
        # Post-optimization: Remove unnecessary waits at start/end
        optimized = self._remove_unnecessary_waits(optimized)
        
        return optimized
    
    def _is_redundant(
        self,
        action: Dict[str, Any],
        prev_action: Optional[Dict[str, Any]],
        optimized: List[Dict[str, Any]]
    ) -> bool:
        """Check if action is redundant"""
        action_type = action.get("action_type", "")
        
        # Very short waits (<0.1s) are usually redundant
        if action_type == "wait":
            duration = action.get("duration", 0)
            if duration < 0.1:
                return True
        
        # Duplicate actions (same type, same selector) are redundant
        if action_type in ["click", "type"] and prev_action:
            if prev_action.get("action_type") == action_type:
                prev_selector = prev_action.get("selector")
                curr_selector = action.get("selector")
                if self._selectors_equal(prev_selector, curr_selector):
                    # Check if text is also the same (for type actions)
                    if action_type == "type":
                        if prev_action.get("text") == action.get("text"):
                            return True
                    else:
                        return True
        
        return False
    
    def _selectors_equal(self, sel1: Any, sel2: Any) -> bool:
        """Check if two selectors are equal"""
        if sel1 is None or sel2 is None:
            return False
        
        # Convert to string for comparison
        return str(sel1) == str(sel2)
    
    def _remove_unnecessary_waits(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove unnecessary waits at start and end of sequence"""
        if not actions:
            return actions
        
        optimized = actions.copy()
        
        # Remove waits at the start (unless they're significant)
        while optimized and optimized[0].get("action_type") == "wait":
            if optimized[0].get("duration", 0) < 0.5:
                optimized.pop(0)
            else:
                break
        
        # Remove waits at the end (unless they're significant)
        while optimized and optimized[-1].get("action_type") == "wait":
            if optimized[-1].get("duration", 0) < 0.5:
                optimized.pop()
            else:
                break
        
        return optimized
    
    def optimize_for_task_type(
        self,
        actions: List[Dict[str, Any]],
        task_type: str
    ) -> List[Dict[str, Any]]:
        """
        Optimize action sequence for specific task type
        Tok-style: Task-specific optimizations
        """
        optimized = self.optimize_sequence(actions)
        
        # Task-specific optimizations
        if task_type == "login":
            # Login tasks: Ensure navigation is first, remove redundant waits
            optimized = self._optimize_login_sequence(optimized)
        elif task_type == "form":
            # Form tasks: Ensure proper field order, remove redundant clicks
            optimized = self._optimize_form_sequence(optimized)
        elif task_type == "search":
            # Search tasks: Optimize search input and button clicks
            optimized = self._optimize_search_sequence(optimized)
        
        return optimized
    
    def _optimize_login_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize login sequence"""
        optimized = []
        has_navigation = False
        
        # Ensure navigation is first
        for action in actions:
            if action.get("action_type") == "navigate" and not has_navigation:
                optimized.append(action)
                has_navigation = True
            elif action.get("action_type") != "navigate" or has_navigation:
                optimized.append(action)
        
        return optimized
    
    def _optimize_form_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize form filling sequence"""
        # Remove redundant clicks before type actions
        optimized = []
        i = 0
        while i < len(actions):
            action = actions[i]
            next_action = actions[i + 1] if i + 1 < len(actions) else None
            
            # If click is followed by type on same selector, keep both
            if (action.get("action_type") == "click" and
                next_action and next_action.get("action_type") == "type" and
                self._selectors_equal(action.get("selector"), next_action.get("selector"))):
                optimized.append(action)
                optimized.append(next_action)
                i += 2
            else:
                optimized.append(action)
                i += 1
        
        return optimized
    
    def _optimize_search_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize search sequence"""
        # Ensure type comes before click for search button
        optimized = []
        type_action = None
        click_action = None
        
        for action in actions:
            if action.get("action_type") == "type":
                type_action = action
            elif action.get("action_type") == "click" and type_action:
                click_action = action
                # Add type before click
                optimized.append(type_action)
                optimized.append(click_action)
                type_action = None
                click_action = None
            else:
                optimized.append(action)
        
        # Add any remaining actions
        if type_action:
            optimized.append(type_action)
        if click_action:
            optimized.append(click_action)
        
        return optimized


# Global instance
action_optimizer = ActionOptimizer()
