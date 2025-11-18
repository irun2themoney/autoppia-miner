"""Smart wait strategies - intelligent wait times based on action type and context"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SmartWaitStrategy:
    """Intelligent wait time calculation based on action type and context"""
    
    # Base wait times by action type (in seconds)
    ACTION_WAITS = {
        "NavigateAction": 1.5,  # Page load time
        "ClickAction": 1.0,     # Element interaction + page update
        "TypeAction": 0.3,      # Text input (fast)
        "WaitAction": 0.0,      # Already a wait, no additional
        "ScreenshotAction": 0.1, # Screenshot capture (very fast)
        "ScrollAction": 0.5,    # Scroll animation
        "GoBackAction": 1.0,    # Page navigation
    }
    
    # Context-based multipliers
    CONTEXT_MULTIPLIERS = {
        "slow_page": 1.5,       # Slow-loading pages
        "fast_page": 0.7,       # Fast pages
        "ajax_heavy": 2.0,      # AJAX-heavy pages
        "form_submit": 2.0,     # Form submissions (longer wait)
        "login": 2.0,           # Login actions (redirects)
        "navigation": 1.5,      # Navigation actions
    }
    
    def __init__(self):
        self.page_speed_history = []  # Track page load times
        self.adaptive_waits = {}      # Learned optimal waits
    
    def get_wait_time(
        self,
        action_type: str,
        context: Optional[Dict[str, Any]] = None,
        previous_action: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Get optimal wait time for an action
        
        Args:
            action_type: Type of action (NavigateAction, ClickAction, etc.)
            context: Optional context (page_type, is_ajax, etc.)
            previous_action: Previous action for sequence optimization
            
        Returns:
            Optimal wait time in seconds
        """
        # Get base wait time
        base_wait = self.ACTION_WAITS.get(action_type, 0.5)
        
        # Apply context multipliers
        if context:
            multiplier = 1.0
            
            # Check for slow/fast page indicators
            if context.get("is_slow_page"):
                multiplier *= self.CONTEXT_MULTIPLIERS.get("slow_page", 1.0)
            elif context.get("is_fast_page"):
                multiplier *= self.CONTEXT_MULTIPLIERS.get("fast_page", 1.0)
            
            # Check for AJAX-heavy pages
            if context.get("is_ajax_heavy"):
                multiplier *= self.CONTEXT_MULTIPLIERS.get("ajax_heavy", 1.0)
            
            # Check for form submissions
            if context.get("is_form_submit"):
                multiplier *= self.CONTEXT_MULTIPLIERS.get("form_submit", 1.0)
            
            # Check for login actions
            if context.get("is_login"):
                multiplier *= self.CONTEXT_MULTIPLIERS.get("login", 1.0)
            
            # Check for navigation
            if context.get("is_navigation"):
                multiplier *= self.CONTEXT_MULTIPLIERS.get("navigation", 1.0)
            
            base_wait *= multiplier
        
        # Optimize based on previous action
        if previous_action:
            prev_type = previous_action.get("type", "")
            
            # If previous was a wait, reduce current wait
            if prev_type == "WaitAction":
                base_wait *= 0.7
            
            # If previous was screenshot, minimal wait needed
            if prev_type == "ScreenshotAction":
                base_wait = min(base_wait, 0.2)
            
            # If previous was type, shorter wait for next type
            if prev_type == "TypeAction" and action_type == "TypeAction":
                base_wait = min(base_wait, 0.2)
        
        # Check for learned optimal waits
        wait_key = f"{action_type}_{context.get('page_type', 'default') if context else 'default'}"
        if wait_key in self.adaptive_waits:
            # Use learned wait with some exploration
            learned_wait = self.adaptive_waits[wait_key]
            # Blend learned and calculated (70% learned, 30% calculated)
            base_wait = learned_wait * 0.7 + base_wait * 0.3
        
        # Ensure minimum wait time
        min_wait = 0.1
        max_wait = 5.0
        
        return max(min_wait, min(base_wait, max_wait))
    
    def get_wait_for_action(
        self,
        action: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        previous_action: Optional[Dict[str, Any]] = None
    ) -> float:
        """Get wait time for a specific action"""
        action_type = action.get("type", "")
        return self.get_wait_time(action_type, context, previous_action)
    
    def record_page_load_time(self, load_time: float):
        """Record page load time for adaptive learning"""
        self.page_speed_history.append(load_time)
        # Keep only last 50 measurements
        if len(self.page_speed_history) > 50:
            self.page_speed_history.pop(0)
    
    def get_page_speed_context(self) -> Dict[str, Any]:
        """Get page speed context based on history"""
        if not self.page_speed_history:
            return {}
        
        avg_load_time = sum(self.page_speed_history) / len(self.page_speed_history)
        
        context = {}
        if avg_load_time > 3.0:
            context["is_slow_page"] = True
        elif avg_load_time < 1.0:
            context["is_fast_page"] = True
        
        return context
    
    def learn_optimal_wait(
        self,
        action_type: str,
        context: Dict[str, Any],
        actual_wait: float,
        success: bool
    ):
        """Learn optimal wait time from experience"""
        wait_key = f"{action_type}_{context.get('page_type', 'default')}"
        
        if success:
            # If successful, this wait time worked well
            if wait_key not in self.adaptive_waits:
                self.adaptive_waits[wait_key] = actual_wait
            else:
                # Update with exponential moving average
                self.adaptive_waits[wait_key] = (
                    self.adaptive_waits[wait_key] * 0.8 + actual_wait * 0.2
                )
        else:
            # If failed, might need longer wait
            if wait_key not in self.adaptive_waits:
                self.adaptive_waits[wait_key] = actual_wait * 1.5
            else:
                # Increase wait slightly
                self.adaptive_waits[wait_key] = min(
                    self.adaptive_waits[wait_key] * 1.1,
                    5.0  # Cap at 5 seconds
                )


# Global instance
smart_wait = SmartWaitStrategy()

