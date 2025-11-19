"""Website-specific error handling and recovery strategies"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class WebsiteErrorHandler:
    """
    Website-specific error handling and recovery strategies
    Tok-style: Different error handling for different websites
    """
    
    def __init__(self):
        self.error_history = {}  # Track errors per website
    
    def get_website_specific_recovery(
        self,
        website: str,
        failed_action: Dict[str, Any],
        error_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get website-specific recovery actions
        
        Tok-style: Different recovery strategies for different websites
        """
        recovery = []
        
        # Website-specific recovery strategies
        if website == "autolist":
            recovery = self._get_autolist_recovery(failed_action, error_type)
        elif website == "autoconnect":
            recovery = self._get_autoconnect_recovery(failed_action, error_type)
        elif website == "automail":
            recovery = self._get_automail_recovery(failed_action, error_type)
        else:
            # Generic recovery for other websites
            recovery = self._get_generic_recovery(failed_action, error_type)
        
        return recovery
    
    def _get_autolist_recovery(self, failed_action: Dict[str, Any], error_type: str) -> List[Dict[str, Any]]:
        """AutoList-specific recovery (Tok's weak point - 50%)"""
        recovery = []
        action_type = failed_action.get("action_type", "")
        
        if action_type == "click" and "add" in str(failed_action.get("selector", "")).lower():
            # Add item button failed - try scrolling first, then retry
            recovery.append({
                "action_type": "scroll",
                "direction": "down",
                "pixels": 300
            })
            recovery.append({
                "action_type": "wait",
                "duration": 1.0
            })
            recovery.append({
                **failed_action,
                "retry": True
            })
        elif action_type == "type":
            # Typing failed - try clicking input first
            selector = failed_action.get("selector")
            if selector:
                recovery.append({
                    "action_type": "click",
                    "selector": selector
                })
                recovery.append({
                    "action_type": "wait",
                    "duration": 0.5
                })
                recovery.append(failed_action)
        
        return recovery
    
    def _get_autoconnect_recovery(self, failed_action: Dict[str, Any], error_type: str) -> List[Dict[str, Any]]:
        """AutoConnect-specific recovery (Tok's weak point - 50%)"""
        recovery = []
        action_type = failed_action.get("action_type", "")
        selector_str = str(failed_action.get("selector", "")).lower()
        
        if action_type == "click" and "job" in selector_str:
            # Job card click failed - try scrolling, then retry
            recovery.append({
                "action_type": "scroll",
                "direction": "down",
                "pixels": 500  # Job listings are long
            })
            recovery.append({
                "action_type": "wait",
                "duration": 1.5
            })
            recovery.append({
                **failed_action,
                "retry": True
            })
        elif action_type == "type" and "search" in selector_str:
            # Search input failed - try clicking search button after typing
            recovery.append(failed_action)
            recovery.append({
                "action_type": "wait",
                "duration": 0.5
            })
            recovery.append({
                "action_type": "click",
                "selector": [{"type": "tagContainsSelector", "value": "Search"}]
            })
        elif action_type == "click":
            # Generic click recovery for AutoConnect
            recovery.append({
                "action_type": "wait",
                "duration": 1.5  # Job pages need more time
            })
            recovery.append({
                **failed_action,
                "retry": True
            })
        else:
            # Generic recovery for other action types
            recovery.append({
                "action_type": "wait",
                "duration": 1.0
            })
            recovery.append({
                **failed_action,
                "retry": True
            })
        
        return recovery
    
    def _get_automail_recovery(self, failed_action: Dict[str, Any], error_type: str) -> List[Dict[str, Any]]:
        """AutoMail-specific recovery (Tok's weak point - 50%)"""
        recovery = []
        action_type = failed_action.get("action_type", "")
        
        if action_type == "click" and "compose" in str(failed_action.get("selector", "")).lower():
            # Compose button failed - try waiting longer, then retry
            recovery.append({
                "action_type": "wait",
                "duration": 2.0  # Mail pages need more time
            })
            recovery.append({
                **failed_action,
                "retry": True
            })
        elif action_type == "type" and ("to" in str(failed_action.get("selector", "")).lower() or 
                                         "subject" in str(failed_action.get("selector", "")).lower()):
            # Email field typing failed - try clicking field first
            selector = failed_action.get("selector")
            if selector:
                recovery.append({
                    "action_type": "click",
                    "selector": selector
                })
                recovery.append({
                    "action_type": "wait",
                    "duration": 0.8
                })
                recovery.append(failed_action)
        elif action_type == "click" and "send" in str(failed_action.get("selector", "")).lower():
            # Send button failed - try scrolling to it first
            recovery.append({
                "action_type": "scroll",
                "direction": "down",
                "pixels": 200
            })
            recovery.append({
                "action_type": "wait",
                "duration": 1.0
            })
            recovery.append({
                **failed_action,
                "retry": True
            })
        
        return recovery
    
    def _get_generic_recovery(self, failed_action: Dict[str, Any], error_type: str) -> List[Dict[str, Any]]:
        """Generic recovery for other websites"""
        recovery = []
        
        # Basic retry with wait
        recovery.append({
            "action_type": "wait",
            "duration": 1.0
        })
        recovery.append({
            **failed_action,
            "retry": True
        })
        
        return recovery
    
    def record_website_error(self, website: str, error_type: str, action_type: str):
        """Record error for learning"""
        key = f"{website}_{error_type}_{action_type}"
        if key not in self.error_history:
            self.error_history[key] = 0
        self.error_history[key] += 1
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            # Remove oldest entries
            oldest_key = min(self.error_history.keys(), key=lambda k: self.error_history[k])
            del self.error_history[oldest_key]


# Global instance
website_error_handler = WebsiteErrorHandler()

