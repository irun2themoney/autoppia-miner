"""Enhanced error recovery and alternative strategies"""
from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ErrorRecovery:
    """
    Enhanced error recovery with alternative strategies
    """
    
    def __init__(self):
        self.error_patterns = {}  # Track error patterns
        self.recovery_strategies = {}  # Learned recovery strategies
    
    def get_alternative_selectors(
        self,
        original_selector: Dict[str, Any],
        element_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get alternative selectors when primary selector fails
        
        Returns:
            List of alternative selectors to try
        """
        alternatives = []
        selector_type = original_selector.get("type", "")
        value = original_selector.get("value", "")
        
        # Generate alternatives based on selector type
        if selector_type == "attributeValueSelector":
            attribute = original_selector.get("attribute", "")
            
            # Try different attributes
            alt_attributes = ["id", "name", "class", "data-testid", "aria-label"]
            for alt_attr in alt_attributes:
                if alt_attr != attribute:
                    alternatives.append({
                        "type": "attributeValueSelector",
                        "value": value,
                        "attribute": alt_attr,
                        "case_sensitive": original_selector.get("case_sensitive", False)
                    })
            
            # Try tagContainsSelector as fallback
            alternatives.append({
                "type": "tagContainsSelector",
                "value": value,
                "case_sensitive": False
            })
        
        elif selector_type == "tagContainsSelector":
            # Try attributeValueSelector with common attributes
            for attr in ["id", "name", "data-testid", "aria-label"]:
                alternatives.append({
                    "type": "attributeValueSelector",
                    "value": value,
                    "attribute": attr,
                    "case_sensitive": False
                })
        
        # Limit alternatives
        return alternatives[:5]
    
    def get_alternative_action(
        self,
        failed_action: Dict[str, Any],
        error_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get alternative action when primary action fails
        
        Returns:
            Alternative action or None
        """
        action_type = failed_action.get("action_type", "")
        
        # Action-specific alternatives
        if action_type == "click":
            # Try alternative selectors
            selector = failed_action.get("selector")
            if selector:
                # Return same action but with alternative selector strategy
                return {
                    **failed_action,
                    "retry": True,
                    "retry_count": failed_action.get("retry_count", 0) + 1
                }
        
        elif action_type == "type":
            # Try clicking field first, then typing
            selector = failed_action.get("selector")
            if selector:
                return {
                    "action_type": "click",
                    "selector": selector
                }
        
        elif action_type == "navigate":
            # Navigation failures are usually fatal
            return None
        
        return None
    
    def should_retry(
        self,
        action: Dict[str, Any],
        error_type: str,
        retry_count: int = 0
    ) -> bool:
        """Determine if action should be retried - Enhanced for better recovery"""
        max_retries = 3  # Increased from 2 to 3 for better recovery
        
        # Don't retry navigation failures (usually fatal)
        if action.get("action_type") == "navigate":
            return False
        
        # Don't retry if already retried too many times
        if retry_count >= max_retries:
            return False
        
        # Retry transient errors (expanded list)
        retryable_errors = [
            "element_not_found",
            "element_not_clickable",
            "element_not_visible",
            "timeout",
            "stale_element",
            "element_not_interactable",
            "invalid_selector",
            "network_error",  # Network issues might be transient
        ]
        
        return error_type in retryable_errors
    
    def get_recovery_actions(
        self,
        failed_action: Dict[str, Any],
        error_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recovery actions for failed action
        
        Returns:
            List of recovery actions
        """
        recovery = []
        action_type = failed_action.get("action_type", "")
        
        # Add wait before retry (increased for better recovery)
        recovery.append({
            "action_type": "wait",
            "duration": 1.5  # Increased from 1.0 to 1.5 for better recovery
        })
        
        # Get alternative action
        alternative = self.get_alternative_action(failed_action, error_type, context)
        if alternative:
            recovery.append(alternative)
        
        # Add screenshot to verify recovery
        recovery.append({
            "action_type": "screenshot"
        })
        
        return recovery
    
    def record_error(
        self,
        action: Dict[str, Any],
        error_type: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record error for learning"""
        action_type = action.get("action_type", "")
        key = f"{action_type}_{error_type}"
        
        if key not in self.error_patterns:
            self.error_patterns[key] = 0
        
        self.error_patterns[key] += 1
    
    def get_error_frequency(self, action_type: str, error_type: str) -> int:
        """Get frequency of specific error"""
        key = f"{action_type}_{error_type}"
        return self.error_patterns.get(key, 0)


# Global instance
error_recovery = ErrorRecovery()
