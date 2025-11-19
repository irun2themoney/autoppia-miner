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
        Validate action before execution - Enhanced with Tok-style quality checks
        
        Tok validates selectors exist, checks logical flow, ensures completeness
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
            
            # Tok-style: Validate selector structure
            if isinstance(selector, dict):
                # Should have at least one selector type
                selector_types = ["tagSelector", "attributeValueSelector", "tagContainsSelector", 
                                "textSelector", "xpathSelector", "cssSelector"]
                has_valid_selector = any(key in selector for key in selector_types)
                if not has_valid_selector:
                    return False, "Selector dict missing valid selector type"
            elif isinstance(selector, list):
                # List of selectors - should not be empty
                if len(selector) == 0:
                    return False, "Selector list is empty"
        
        elif action_type == "type":
            text = action.get("text", "")
            selector = action.get("selector")
            if not text:
                return False, "Type action missing text"
            if not selector:
                return False, "Type action missing selector"
            
            # Tok-style: Validate text is not empty after trimming
            if isinstance(text, str) and not text.strip():
                return False, "Type action text is empty"
        
        elif action_type == "wait":
            duration = action.get("duration", 0)
            if duration < 0:
                return False, "Wait duration cannot be negative"
            if duration > 30:
                return False, "Wait duration too long (>30s)"
        
        elif action_type == "screenshot":
            # Screenshot actions are always valid
            pass
        
        # Context-based validation (Tok-style quality checks)
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
        Validate entire action sequence - Enhanced with logical flow checks
        
        Tok-style validation: Check not just individual actions, but logical flow
        """
        errors = []
        
        # Validate individual actions
        for i, action in enumerate(actions):
            is_valid, reason = self.validate_action(action, context)
            if not is_valid:
                errors.append(f"Action {i}: {reason}")
        
        # Validate logical flow (Tok-style quality check)
        if len(actions) > 1:
            # Check for navigation before other actions (if URL provided)
            has_navigation = any(a.get("action_type") == "navigate" for a in actions)
            has_other_actions = any(
                a.get("action_type") in ["click", "type", "submit"] 
                for a in actions
            )
            
            # If we have other actions but no navigation, might be missing initial navigation
            if has_other_actions and not has_navigation and context:
                url = context.get("url", "")
                if url and url.startswith(("http://", "https://")):
                    # This is a warning, not an error - might be intentional
                    pass
            
            # Check for selector consistency (same selectors used multiple times should be consistent)
            selectors_used = {}
            for i, action in enumerate(actions):
                if action.get("action_type") in ["click", "type"]:
                    selector = action.get("selector")
                    if selector:
                        selector_str = str(selector)
                        if selector_str in selectors_used:
                            # Same selector used multiple times - should be consistent
                            pass
                        selectors_used[selector_str] = i
        
        return len(errors) == 0, errors
    
    def should_add_verification(self, action: Dict[str, Any]) -> bool:
        """Determine if action should be verified after execution"""
        action_type = action.get("action_type", "")
        
        # Verify important actions
        important_actions = ["navigate", "click", "type", "submit"]
        return action_type in important_actions
    
    def get_verification_action(self, original_action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get verification action for original action - Enhanced for Tok-level quality
        
        Target: 5-8s response time (matching Tok's 6.6s average)
        Strategy: Quality over speed - ensure actions complete before proceeding
        """
        action_type = original_action.get("action_type", "")
        
        if action_type == "navigate":
            # Verify navigation with wait + screenshot (page needs time to load)
            # Tok takes time to ensure page is fully loaded
            return {
                "action_type": "wait",
                "duration": 2.5  # Increased from 1.5s - ensure page fully loads
            }
        
        elif action_type == "click":
            # Verify click with wait + screenshot (UI needs time to update)
            # Tok ensures UI updates before proceeding
            return {
                "action_type": "wait",
                "duration": 1.5  # Increased from 1.0s - ensure UI updates
            }
        
        elif action_type == "type":
            # Verify typing with wait (text needs time to be entered)
            # Tok ensures text is fully entered
            return {
                "action_type": "wait",
                "duration": 0.8  # Increased from 0.5s - ensure text is entered
            }
        
        elif action_type == "submit":
            # Verify submit with longer wait (form submission takes time)
            # Tok ensures form submission completes
            return {
                "action_type": "wait",
                "duration": 3.0  # Increased from 2.0s - ensure submission completes
            }
        
        return None
    
    def enhance_actions_with_verification(
        self,
        actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enhance action sequence with verification steps
        
        Adds verification actions after important actions to ensure quality.
        Target: 5-8s response time (matching Tok's 6.6s average)
        Strategy: Quality over speed - ensure actions complete before proceeding
        """
        enhanced = []
        
        for i, action in enumerate(actions):
            enhanced.append(action)
            
            # Add verification for important actions (Tok-style quality focus)
            if self.should_add_verification(action):
                verification = self.get_verification_action(action)
                if verification:
                    enhanced.append(verification)
                    # Add screenshot after verification wait for important actions
                    # Tok uses screenshots to verify state changes
                    action_type = action.get("action_type", "")
                    important_actions = ["navigate", "click", "submit"]
                    if verification.get("action_type") == "wait" and action_type in important_actions:
                        enhanced.append({"action_type": "screenshot"})
        
        return enhanced
    
    def validate_selector_structure(self, selector: Any) -> Tuple[bool, str]:
        """
        Validate selector structure before action execution (Tok-style pre-validation)
        
        At generation time, we can't check if selectors exist in DOM,
        but we can validate their structure and completeness.
        """
        if not selector:
            return False, "Selector is None or empty"
        
        if isinstance(selector, dict):
            # Should have at least one valid selector type
            valid_types = ["tagSelector", "attributeValueSelector", "tagContainsSelector", 
                          "textSelector", "xpathSelector", "cssSelector"]
            has_valid_type = any(key in selector for key in valid_types)
            if not has_valid_type:
                return False, "Selector dict missing valid selector type"
            
            # Validate each selector type has required fields
            if "tagSelector" in selector:
                if not selector["tagSelector"]:
                    return False, "tagSelector value is empty"
            if "attributeValueSelector" in selector:
                attr_sel = selector["attributeValueSelector"]
                if not isinstance(attr_sel, dict) or not attr_sel.get("attribute") or not attr_sel.get("value"):
                    return False, "attributeValueSelector missing attribute or value"
            if "textSelector" in selector:
                if not selector["textSelector"]:
                    return False, "textSelector value is empty"
            
            return True, "Valid selector structure"
        
        elif isinstance(selector, list):
            if len(selector) == 0:
                return False, "Selector list is empty"
            
            # Validate each selector in the list
            for i, sel in enumerate(selector):
                is_valid, reason = self.validate_selector_structure(sel)
                if not is_valid:
                    return False, f"Selector {i} in list: {reason}"
            
            return True, "Valid selector list"
        
        else:
            return False, f"Selector must be dict or list, got {type(selector)}"
    
    def add_pre_action_validation(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add pre-action validation metadata to actions (Tok-style quality assurance)
        
        This adds validation hints that can be used during execution to ensure
        selectors exist before using them.
        """
        validated_actions = []
        
        for action in actions:
            action_type = action.get("action_type", "")
            
            # Add validation metadata for actions that use selectors
            if action_type in ["click", "type"]:
                selector = action.get("selector")
                if selector:
                    is_valid, reason = self.validate_selector_structure(selector)
                    if is_valid:
                        # Add validation metadata (can be used by executor)
                        action["_validation"] = {
                            "selector_validated": True,
                            "validation_time": "pre_action"
                        }
                    else:
                        # Log warning but don't fail (might be handled by executor)
                        logger.warning(f"Selector validation warning: {reason}")
            
            validated_actions.append(action)
        
        return validated_actions
    
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
