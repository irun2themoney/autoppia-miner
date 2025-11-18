"""Advanced selector intelligence - ranking, validation, and learning"""
from typing import Dict, Any, List, Optional, Tuple
import re
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class SelectorIntelligence:
    """
    Intelligent selector system that:
    - Ranks selectors by reliability
    - Validates selectors before use
    - Learns which selectors work best
    """
    
    # Selector type reliability scores (higher = more reliable)
    SELECTOR_RELIABILITY = {
        "tagContainsSelector": 0.9,      # Text matching - very reliable
        "attributeValueSelector": 0.85,   # Attribute matching - reliable
        "xpathSelector": 0.7,            # XPath - less reliable (fragile)
        "tagSelector": 0.6,              # Tag only - less specific
        "cssSelector": 0.8,              # CSS - reliable
    }
    
    # Attribute reliability scores
    ATTRIBUTE_RELIABILITY = {
        "data-testid": 0.95,    # Test IDs - most reliable
        "id": 0.9,              # IDs - very reliable
        "name": 0.85,           # Name attributes - reliable
        "aria-label": 0.8,      # ARIA labels - reliable
        "class": 0.6,           # Classes - less reliable (can change)
        "type": 0.7,            # Type attributes - moderate
    }
    
    def __init__(self):
        self.selector_success_rates = defaultdict(lambda: {"success": 0, "total": 0})
        self.selector_rankings = {}  # Cached rankings
        self.learned_patterns = {}  # Learned selector patterns
    
    def rank_selectors(
        self,
        selectors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank selectors by reliability and success rate
        
        Returns:
            List of (selector, score) tuples, sorted by score (highest first)
        """
        if not selectors:
            return []
        
        ranked = []
        
        for selector in selectors:
            score = self._calculate_selector_score(selector, context)
            ranked.append((selector, score))
        
        # Sort by score (highest first)
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked
    
    def _calculate_selector_score(
        self,
        selector: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate reliability score for a selector"""
        selector_type = selector.get("type", "")
        score = 0.0
        
        # Base reliability from selector type
        base_reliability = self.SELECTOR_RELIABILITY.get(selector_type, 0.5)
        score += base_reliability * 0.6  # 60% weight
        
        # Attribute reliability (if applicable)
        if selector_type == "attributeValueSelector":
            attribute = selector.get("attribute", "")
            attr_reliability = self.ATTRIBUTE_RELIABILITY.get(attribute, 0.5)
            score += attr_reliability * 0.3  # 30% weight
        
        # Historical success rate (if available)
        selector_key = self._get_selector_key(selector)
        if selector_key in self.selector_success_rates:
            stats = self.selector_success_rates[selector_key]
            if stats["total"] > 0:
                success_rate = stats["success"] / stats["total"]
                score += success_rate * 0.1  # 10% weight
        
        # Context bonuses
        if context:
            # Bonus for selectors matching context
            if context.get("is_login_page") and selector_type == "attributeValueSelector":
                if selector.get("attribute") in ["name", "id"]:
                    score += 0.05  # Login pages prefer name/id
            
            if context.get("is_form_page") and selector_type == "attributeValueSelector":
                if selector.get("attribute") in ["name", "type"]:
                    score += 0.05  # Forms prefer name/type
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_selector_key(self, selector: Dict[str, Any]) -> str:
        """Generate a key for selector tracking"""
        selector_type = selector.get("type", "")
        value = selector.get("value", "")
        attribute = selector.get("attribute", "")
        
        return f"{selector_type}:{attribute}:{value}"
    
    def validate_selector(
        self,
        selector: Dict[str, Any],
        page_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Validate if a selector makes sense for the context
        
        Returns:
            (is_valid, reason)
        """
        selector_type = selector.get("type", "")
        value = selector.get("value", "")
        
        # Basic validation
        if not selector_type:
            return False, "Missing selector type"
        
        if not value:
            return False, "Missing selector value"
        
        # Type-specific validation
        if selector_type == "attributeValueSelector":
            attribute = selector.get("attribute", "")
            if not attribute:
                return False, "Attribute selector missing attribute"
            
            # Validate attribute name
            valid_attributes = [
                "name", "id", "type", "class", "data-testid", "aria-label",
                "data-cy", "role", "href", "src"
            ]
            if attribute not in valid_attributes:
                return False, f"Invalid attribute: {attribute}"
        
        elif selector_type == "xpathSelector":
            # Basic XPath validation
            if not value.startswith(("//", "/", ".//", "./")):
                return False, "Invalid XPath format"
        
        elif selector_type == "tagContainsSelector":
            # Text should not be empty
            if len(value.strip()) == 0:
                return False, "Empty text for tagContainsSelector"
        
        # Context-based validation
        if page_context:
            # Check if selector matches page type
            if page_context.get("is_login_page"):
                # Login pages should use name/id/type attributes
                if selector_type == "attributeValueSelector":
                    attribute = selector.get("attribute", "")
                    if attribute not in ["name", "id", "type"]:
                        return False, f"Login page selector should use name/id/type, got {attribute}"
        
        return True, "Valid"
    
    def get_best_selectors(
        self,
        selectors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        max_selectors: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get the best selectors, ranked and validated
        
        Returns:
            List of best selectors (up to max_selectors)
        """
        if not selectors:
            return []
        
        # Rank selectors
        ranked = self.rank_selectors(selectors, context)
        
        # Filter and validate
        best = []
        for selector, score in ranked:
            if len(best) >= max_selectors:
                break
            
            # Validate selector
            is_valid, reason = self.validate_selector(selector, context)
            if is_valid:
                best.append(selector)
            else:
                logger.debug(f"Selector invalid: {reason} - {selector}")
        
        # If we don't have enough valid selectors, add invalid ones as fallback
        if len(best) < max_selectors:
            for selector, score in ranked:
                if len(best) >= max_selectors:
                    break
                if selector not in best:
                    best.append(selector)
        
        return best
    
    def record_selector_success(
        self,
        selector: Dict[str, Any],
        success: bool,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record selector success/failure for learning"""
        selector_key = self._get_selector_key(selector)
        
        self.selector_success_rates[selector_key]["total"] += 1
        if success:
            self.selector_success_rates[selector_key]["success"] += 1
        
        # Invalidate cached rankings
        if selector_key in self.selector_rankings:
            del self.selector_rankings[selector_key]
    
    def get_selector_success_rate(self, selector: Dict[str, Any]) -> float:
        """Get historical success rate for a selector"""
        selector_key = self._get_selector_key(selector)
        
        if selector_key in self.selector_success_rates:
            stats = self.selector_success_rates[selector_key]
            if stats["total"] > 0:
                return stats["success"] / stats["total"]
        
        return 0.5  # Default 50% if no history
    
    def learn_pattern(
        self,
        element_type: str,
        successful_selectors: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ):
        """Learn which selector patterns work best for element types"""
        if not successful_selectors:
            return
        
        # Find the most successful selector
        best_selector = None
        best_score = 0.0
        
        for selector in successful_selectors:
            score = self._calculate_selector_score(selector, context)
            if score > best_score:
                best_score = score
                best_selector = selector
        
        if best_selector:
            pattern_key = f"{element_type}_{context.get('page_type', 'generic') if context else 'generic'}"
            self.learned_patterns[pattern_key] = {
                "selector": best_selector,
                "score": best_score,
                "count": self.learned_patterns.get(pattern_key, {}).get("count", 0) + 1
            }
    
    def get_learned_pattern(
        self,
        element_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get learned selector pattern for element type"""
        pattern_key = f"{element_type}_{context.get('page_type', 'generic') if context else 'generic'}"
        
        if pattern_key in self.learned_patterns:
            return self.learned_patterns[pattern_key].get("selector")
        
        return None


# Global instance
selector_intelligence = SelectorIntelligence()

