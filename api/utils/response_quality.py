"""Response quality improvements for better accuracy and success rates"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ResponseQualityEnhancer:
    """Enhance response quality for better validator rewards"""
    
    def __init__(self):
        self.quality_checks = []
    
    def validate_action_quality(self, action: Dict[str, Any]) -> bool:
        """Validate individual action quality"""
        action_type = action.get("type", "")
        
        # Check required fields based on action type
        if action_type == "ClickAction":
            if not action.get("selector"):
                return False
            selector = action["selector"]
            if isinstance(selector, dict):
                if not selector.get("value"):
                    return False
        
        elif action_type == "TypeAction":
            if not action.get("text"):
                return False
            if not action.get("selector"):
                return False
        
        elif action_type == "NavigateAction":
            if not action.get("url"):
                return False
        
        elif action_type == "WaitAction":
            if not action.get("time_seconds"):
                return False
        
        return True
    
    def enhance_action_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance action sequence for better quality"""
        enhanced = []
        
        for i, action in enumerate(actions):
            # Validate action quality
            if not self.validate_action_quality(action):
                logger.warning(f"Skipping invalid action at index {i}: {action.get('type', 'unknown')}")
                continue
            
            # Enhance action with better defaults
            enhanced_action = self._enhance_action(action, i, actions)
            enhanced.append(enhanced_action)
        
        return enhanced
    
    def _enhance_action(self, action: Dict[str, Any], index: int, all_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance individual action"""
        action_type = action.get("type", "")
        enhanced = action.copy()
        
        # Add verification steps after critical actions
        if action_type == "NavigateAction":
            # Ensure wait after navigation
            if index + 1 < len(all_actions):
                next_action = all_actions[index + 1]
                if next_action.get("type") != "WaitAction":
                    # Will be added by optimizer
                    pass
        
        # Ensure proper selector format
        if "selector" in enhanced and isinstance(enhanced["selector"], dict):
            selector = enhanced["selector"]
            # Ensure case_sensitive is set
            if "case_sensitive" not in selector:
                selector["case_sensitive"] = False
            
            # Ensure attribute is set for attributeValueSelector
            if selector.get("type") == "attributeValueSelector" and not selector.get("attribute"):
                # Try to infer attribute
                value = selector.get("value", "")
                if value.startswith("#"):
                    selector["attribute"] = "id"
                    selector["value"] = value[1:]
                elif value.startswith("."):
                    selector["attribute"] = "class"
                    selector["value"] = value[1:]
                else:
                    selector["attribute"] = "name"
        
        return enhanced
    
    def calculate_quality_score(self, actions: List[Dict[str, Any]]) -> float:
        """Calculate quality score for action sequence"""
        if not actions:
            return 0.0
        
        score = 0.0
        total = len(actions)
        
        # Check for required actions
        has_navigate = any(a.get("type") == "NavigateAction" for a in actions)
        has_screenshot = any(a.get("type") == "ScreenshotAction" for a in actions)
        
        if has_navigate:
            score += 0.2
        if has_screenshot:
            score += 0.1
        
        # Check action validity
        valid_actions = sum(1 for a in actions if self.validate_action_quality(a))
        score += (valid_actions / total) * 0.7
        
        return min(score, 1.0)

