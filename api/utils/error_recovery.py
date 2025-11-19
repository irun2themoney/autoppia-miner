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
        Get alternative action when primary action fails - Enhanced with more strategies
        Tok-style: Multiple alternative strategies for better recovery
        """
        action_type = failed_action.get("action_type", "")
        
        # Action-specific alternatives (enhanced strategies)
        if action_type == "click":
            selector = failed_action.get("selector")
            if selector:
                # Strategy 1: Try alternative selectors (already handled by get_alternative_selectors)
                # Strategy 2: Try clicking parent element
                # Strategy 3: Try scrolling to element first, then clicking
                retry_count = failed_action.get("retry_count", 0)
                
                if retry_count == 0:
                    # First retry: Try with alternative selector strategy
                    return {
                        **failed_action,
                        "retry": True,
                        "retry_count": retry_count + 1,
                        "_alternative_strategy": "alternative_selector"
                    }
                elif retry_count == 1:
                    # Second retry: Try scrolling first
                    return {
                        "action_type": "scroll",
                        "direction": "down",
                        "pixels": 200
                    }
                else:
                    # Third retry: Try clicking with wait
                    return {
                        **failed_action,
                        "retry": True,
                        "retry_count": retry_count + 1,
                        "_wait_before": 1.0  # Wait before clicking
                    }
        
        elif action_type == "type":
            selector = failed_action.get("selector")
            text = failed_action.get("text", "")
            retry_count = failed_action.get("retry_count", 0)
            
            if selector:
                if retry_count == 0:
                    # First retry: Try clicking field first, then typing
                    return {
                        "action_type": "click",
                        "selector": selector
                    }
                elif retry_count == 1:
                    # Second retry: Try clearing field first, then typing
                    return {
                        "action_type": "type",
                        "selector": selector,
                        "text": "",  # Clear first
                        "retry": True,
                        "retry_count": retry_count + 1
                    }
                else:
                    # Third retry: Try with longer wait
                    return {
                        "action_type": "wait",
                        "duration": 1.5
                    }
        
        elif action_type == "submit":
            # Submit failures: Try clicking submit button explicitly
            selector = failed_action.get("selector")
            if selector:
                return {
                    "action_type": "click",
                    "selector": selector,
                    "retry": True
                }
        
        elif action_type == "navigate":
            # Navigation failures are usually fatal, but try once more
            retry_count = failed_action.get("retry_count", 0)
            if retry_count == 0:
                return {
                    **failed_action,
                    "retry": True,
                    "retry_count": retry_count + 1
                }
            return None
        
        return None
    
    def should_retry(
        self,
        action: Dict[str, Any],
        error_type: str,
        retry_count: int = 0,
        task_type: Optional[str] = None
    ) -> bool:
        """
        Determine if action should be retried - Enhanced with task-specific retry logic
        Tok-style: Different retry strategies for different task types
        """
        action_type = action.get("action_type", "")
        
        # Task-specific max retries (Tok-style: different retries for different tasks)
        task_specific_retries = {
            "login": 2,  # Login failures are usually fatal, fewer retries
            "form": 3,   # Forms can have transient issues, more retries
            "click": 3,  # Clicks can fail due to timing, more retries
            "type": 2,   # Typing failures are usually selector issues, fewer retries
            "navigate": 1,  # Navigation failures are usually fatal, minimal retries
            "search": 3,  # Search can have timing issues, more retries
            "job_apply": 3,  # Job applications can have complex flows, more retries
        }
        
        max_retries = task_specific_retries.get(task_type or action_type, 3)
        
        # Don't retry navigation failures (usually fatal)
        if action_type == "navigate":
            return False
        
        # Don't retry if already retried too many times
        if retry_count >= max_retries:
            return False
        
        # Task-specific retryable errors (Tok-style: different errors for different tasks)
        retryable_errors_by_task = {
            "login": [
                "element_not_found",
                "element_not_clickable",
                "timeout",
                "stale_element",
            ],
            "form": [
                "element_not_found",
                "element_not_clickable",
                "element_not_visible",
                "timeout",
                "stale_element",
                "element_not_interactable",
            ],
            "click": [
                "element_not_found",
                "element_not_clickable",
                "element_not_visible",
                "timeout",
                "stale_element",
                "element_not_interactable",
            ],
            "type": [
                "element_not_found",
                "element_not_visible",
                "timeout",
                "stale_element",
            ],
            "search": [
                "element_not_found",
                "element_not_clickable",
                "timeout",
                "stale_element",
            ],
        }
        
        # Get task-specific retryable errors, fallback to general list
        retryable_errors = retryable_errors_by_task.get(
            task_type or action_type,
            [
                "element_not_found",
                "element_not_clickable",
                "element_not_visible",
                "timeout",
                "stale_element",
                "element_not_interactable",
                "invalid_selector",
                "network_error",
            ]
        )
        
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
