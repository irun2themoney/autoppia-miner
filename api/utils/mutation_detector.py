"""Mutation detection for Dynamic 3 - handles evolving sites"""
import logging
from typing import Dict, Any, List, Optional
import hashlib

logger = logging.getLogger(__name__)


class MutationDetector:
    """
    Detects site mutations and adapts selectors
    Critical for Dynamic 3: sites evolve every cycle
    """
    
    def __init__(self):
        self.selector_history: Dict[str, List[Dict[str, Any]]] = {}
        self.mutation_patterns: Dict[str, int] = {}
    
    def detect_mutation(
        self,
        selector: Dict[str, Any],
        action_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Detect if a selector has mutated (site changed)
        Returns True if mutation detected
        """
        selector_key = self._get_selector_key(selector)
        
        if selector_key not in self.selector_history:
            # First time seeing this selector
            self.selector_history[selector_key] = [selector]
            return False
        
        # Check if selector pattern has changed
        history = self.selector_history[selector_key]
        if len(history) > 1:
            # Compare with previous patterns
            last_pattern = history[-1]
            if self._compare_selectors(selector, last_pattern):
                # Pattern changed - mutation detected
                self.mutation_patterns[selector_key] = self.mutation_patterns.get(selector_key, 0) + 1
                logger.warning(f"Mutation detected for {action_type} selector")
                return True
        
        return False
    
    def get_adaptive_selector(
        self,
        original_selector: Dict[str, Any],
        action_type: str,
        prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Generate adaptive selectors that handle mutations
        Returns list of selector strategies (fallback chain)
        """
        selectors = [original_selector]
        
        # If mutation detected, add more robust alternatives
        selector_key = self._get_selector_key(original_selector)
        mutation_count = self.mutation_patterns.get(selector_key, 0)
        
        if mutation_count > 0:
            # Site mutates frequently - use more flexible selectors
            logger.info(f"Using adaptive selectors (mutation count: {mutation_count})")
            
            # Add XPath alternatives
            if original_selector.get("type") != "xpathSelector":
                value = original_selector.get("value", "")
                if value:
                    # Generate XPath alternatives
                    xpath_selectors = self._generate_xpath_alternatives(value, action_type)
                    selectors.extend(xpath_selectors)
            
            # Add attribute-based alternatives
            if original_selector.get("type") == "tagContainsSelector":
                value = original_selector.get("value", "")
                # Try data attributes
                selectors.append({
                    "type": "attributeValueSelector",
                    "value": value.lower().replace(" ", "-"),
                    "attribute": "data-testid",
                    "case_sensitive": False
                })
                selectors.append({
                    "type": "attributeValueSelector",
                    "value": value.lower(),
                    "attribute": "aria-label",
                    "case_sensitive": False
                })
        
        return selectors
    
    def _get_selector_key(self, selector: Dict[str, Any]) -> str:
        """Generate a key for selector tracking"""
        selector_str = f"{selector.get('type')}:{selector.get('value', '')}"
        return hashlib.md5(selector_str.encode()).hexdigest()[:8]
    
    def _compare_selectors(
        self,
        selector1: Dict[str, Any],
        selector2: Dict[str, Any]
    ) -> bool:
        """Compare two selectors to detect changes"""
        # Simple comparison - check if key attributes changed
        if selector1.get("type") != selector2.get("type"):
            return True
        
        if selector1.get("value") != selector2.get("value"):
            return True
        
        return False
    
    def _generate_xpath_alternatives(
        self,
        value: str,
        action_type: str
    ) -> List[Dict[str, Any]]:
        """Generate XPath alternatives for mutation resilience"""
        alternatives = []
        
        # Common XPath patterns
        if action_type == "click":
            # Button/link patterns
            alternatives.append({
                "type": "xpathSelector",
                "value": f"//button[contains(text(), '{value}')]",
                "case_sensitive": False
            })
            alternatives.append({
                "type": "xpathSelector",
                "value": f"//a[contains(text(), '{value}')]",
                "case_sensitive": False
            })
            alternatives.append({
                "type": "xpathSelector",
                "value": f"//*[@class='{value.lower().replace(' ', '-')}']",
                "case_sensitive": False
            })
        elif action_type == "type":
            # Input field patterns
            alternatives.append({
                "type": "xpathSelector",
                "value": f"//input[@name='{value.lower()}']",
                "case_sensitive": False
            })
            alternatives.append({
                "type": "xpathSelector",
                "value": f"//input[@type='{value.lower()}']",
                "case_sensitive": False
            })
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def record_selector_success(
        self,
        selector: Dict[str, Any],
        success: bool
    ):
        """Record selector success/failure for learning"""
        selector_key = self._get_selector_key(selector)
        
        if success:
            # Reset mutation count on success
            if selector_key in self.mutation_patterns:
                self.mutation_patterns[selector_key] = max(0, self.mutation_patterns[selector_key] - 1)
        else:
            # Increment on failure (might be mutation)
            self.mutation_patterns[selector_key] = self.mutation_patterns.get(selector_key, 0) + 1

