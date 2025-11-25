"""
Adaptive Selector System - Learns and improves selector generation

This module:
1. Tracks selector success rates
2. Learns which selector types work best for different elements
3. Adapts selector generation based on learned patterns
4. Improves selector accuracy over time
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from .learning_system import get_learning_system

logger = logging.getLogger(__name__)


class AdaptiveSelector:
    """
    Adaptive selector system that learns and improves
    """
    
    def __init__(self):
        self.learning_system = get_learning_system()
        self.selector_preferences = {
            "button": ["attributeValueSelector", "tagContainsSelector", "cssSelector"],
            "input": ["attributeValueSelector", "cssSelector", "xpathSelector"],
            "link": ["tagContainsSelector", "attributeValueSelector", "cssSelector"],
            "form": ["attributeValueSelector", "cssSelector", "xpathSelector"],
            "default": ["attributeValueSelector", "tagContainsSelector", "cssSelector"],
        }
    
    def get_best_selector_strategy(
        self,
        element_type: str,
        element_text: Optional[str] = None,
        element_attributes: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Get best selector strategy for an element based on learned patterns
        
        Args:
            element_type: Type of element (button, input, link, etc.)
            element_text: Text content of element
            element_attributes: Element attributes (id, name, class, etc.)
            
        Returns:
            List of selector types in order of preference
        """
        # Get learned preferences for this element type
        base_preferences = self.selector_preferences.get(
            element_type.lower(),
            self.selector_preferences["default"]
        )
        
        # Get best performing selectors from learning system
        best_selectors = self.learning_system.get_best_selectors(element_type, limit=3)
        
        # Merge learned preferences with base preferences
        learned_types = [s[0].split(":")[0] for s in best_selectors if s[1] > 0.5]
        
        # Prioritize learned selectors with high success rates
        if learned_types:
            # Combine learned and base preferences
            combined = learned_types + [p for p in base_preferences if p not in learned_types]
            return combined[:5]  # Return top 5 strategies
        
        return base_preferences
    
    def should_prefer_attribute_selector(
        self,
        attributes: Dict[str, str]
    ) -> bool:
        """
        Determine if attribute selector should be preferred
        
        Args:
            attributes: Element attributes
            
        Returns:
            True if attribute selector should be preferred
        """
        # Prefer attribute selector if we have id, name, or data-testid
        preferred_attrs = ["id", "name", "data-testid", "data-id"]
        
        for attr in preferred_attrs:
            if attr in attributes and attributes[attr]:
                # Check if this attribute selector has good success rate
                selector_key = f"attributeValueSelector:{attr}:{attributes[attr][:50]}"
                success_rate = self.learning_system.get_selector_success_rate({
                    "type": "attributeValueSelector",
                    "attribute": attr,
                    "value": attributes[attr],
                })
                
                if success_rate > 0.5:
                    return True
        
        return False
    
    def adapt_selector_based_on_feedback(
        self,
        selector: Dict[str, Any],
        success: bool
    ) -> Dict[str, Any]:
        """
        Adapt selector based on execution feedback
        
        Args:
            selector: Original selector
            success: Whether selector succeeded
            
        Returns:
            Potentially improved selector
        """
        if success:
            # Selector worked - keep it as is
            return selector
        
        # Selector failed - try to improve it
        selector_type = selector.get("type", "")
        value = selector.get("value", "")
        
        # If value is empty, try to generate a better one
        if not value or len(value.strip()) == 0:
            logger.warning("⚠️ Empty selector value detected - cannot adapt")
            return selector
        
        # If tagContainsSelector failed, try attributeValueSelector
        if selector_type == "tagContainsSelector":
            logger.info("🔄 Adapting: tagContainsSelector failed, considering alternatives")
            # Could try to find element attributes and use attributeValueSelector
            # For now, just log the adaptation opportunity
        
        return selector
    
    def get_selector_confidence(
        self,
        selector: Dict[str, Any]
    ) -> float:
        """
        Get confidence score for a selector based on learned patterns
        
        Args:
            selector: Selector dictionary
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        success_rate = self.learning_system.get_selector_success_rate(selector)
        
        # Boost confidence if selector has non-empty value
        value = selector.get("value", "")
        if value and len(value.strip()) > 0:
            confidence = success_rate * 1.1  # Boost by 10%
        else:
            confidence = success_rate * 0.5  # Reduce by 50% if empty
        
        return min(confidence, 1.0)  # Cap at 1.0


# Global adaptive selector instance
_adaptive_selector: Optional[AdaptiveSelector] = None


def get_adaptive_selector() -> AdaptiveSelector:
    """Get or create global adaptive selector instance"""
    global _adaptive_selector
    if _adaptive_selector is None:
        _adaptive_selector = AdaptiveSelector()
    return _adaptive_selector

