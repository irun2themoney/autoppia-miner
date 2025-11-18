"""Action validation and verification for quality assurance"""
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ActionValidator:
    """
    Validates actions before execution and verifies after execution
    to ensure quality and accuracy
    """
    
    def __init__(self):
        self.validation_history = []  # Track validation results
    
    def validate_action(self, action: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """
        Validate action before execution
        
        Returns:
            (is_valid, reason)
        """
        action_type = action.get("action_type", "")
        
        # Basic validation
        if not action_type:
            return False, "Missing action_type"
        
        # Type-specific validation
        if action_type == "navigate":
            url = action.get("url", "")
            if not url:
                return False, "Navigate action missing URL"
            if not url.startswith(("http://", "https://")):
                return False, f"Invalid URL format: {url}"
        
        elif action_type == "click":
            selector = action.get("selector")
            if not selector:
                return False, "Click action missing selector"
            if not isinstance(selector, (dict, list)):
                return False, "Selector must be dict or list"
        
        elif action_type == "type":
            text = action.get("text", "")
            selector = action.get("selector")
            if not text:
                return False, "Type action missing text"
            if not selector:
                return False, "Type action missing selector"
        
        elif action_type == "wait":
            duration = action.get("duration", 0)
            if duration < 0:
                return False, "Wait duration cannot be negative"
            if duration > 30:
                return False, "Wait duration too long (>30s)"
        
        elif action_type == "screenshot":
            # Screenshot actions are always valid
            pass
        
        # Context-based validation
        if context:
            # Check if action makes sense for context
            if context.get("is_login_page") and action_type == "navigate":
                # Navigation after login might be expected
                pass
        
        return True, "Valid"
    
    def validate_action_sequence(
        self,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate entire action sequence
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        for i, action in enumerate(actions):
            is_valid, reason = self.validate_action(action, context)
            if not is_valid:
                errors.append(f"Action {i}: {reason}")
        
        return len(errors) == 0, errors
    
    def should_add_verification(self, action: Dict[str, Any]) -> bool:
        """Determine if action should be verified after execution"""
        action_type = action.get("action_type", "")
        
        # Verify important actions
        important_actions = ["navigate", "click", "type", "submit"]
        return action_type in important_actions
    
    def get_verification_action(self, original_action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get verification action for original action - Enhanced for quality"""
        action_type = original_action.get("action_type", "")
        
        if action_type == "navigate":
            # Verify navigation with wait + screenshot (page needs time to load)
            return {
                "action_type": "wait",
                "duration": 1.5  # Give page time to load
            }
        
        elif action_type == "click":
            # Verify click with wait + screenshot (UI needs time to update)
            return {
                "action_type": "wait",
                "duration": 1.0  # Increased for better quality
            }
        
        elif action_type == "type":
            # Verify typing with wait (text needs time to be entered)
            return {
                "action_type": "wait",
                "duration": 0.5  # Increased for better quality
            }
        
        elif action_type == "submit":
            # Verify submit with longer wait (form submission takes time)
            return {
                "action_type": "wait",
                "duration": 2.0  # Form submissions need more time
            }
        
        return None
    
    def enhance_actions_with_verification(
        self,
        actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enhance action sequence with verification steps
        
        Adds verification actions after important actions to ensure quality.
        Balances speed with quality (target 2-5s response time).
        """
        enhanced = []
        
        for i, action in enumerate(actions):
            enhanced.append(action)
            
            # Add verification if needed (but not for every action to balance speed)
            if self.should_add_verification(action):
                verification = self.get_verification_action(action)
                if verification:
                    enhanced.append(verification)
                    # Add screenshot after verification wait for important actions
                    action_type = action.get("action_type", "")
                    important_actions = ["navigate", "click", "submit"]
                    if verification.get("action_type") == "wait" and action_type in important_actions:
                        enhanced.append({"action_type": "screenshot"})
        
        return enhanced
    
    def record_validation(self, action: Dict[str, Any], is_valid: bool, reason: str):
        """Record validation result for learning"""
        self.validation_history.append({
            "action": action,
            "is_valid": is_valid,
            "reason": reason
        })
        
        # Keep only last 100 validations
        if len(self.validation_history) > 100:
            self.validation_history.pop(0)


# Global instance
action_validator = ActionValidator()
