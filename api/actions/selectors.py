"""Selector creation and strategies"""
from typing import Dict, Any, List
from ..utils.keywords import extract_keywords


def create_selector(
    selector_type: str, 
    value: str, 
    attribute: str = None, 
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """Create IWA selector object"""
    selector = {
        "type": selector_type,
        "value": value,
        "case_sensitive": case_sensitive
    }
    if attribute:
        selector["attribute"] = attribute
    return selector


class SelectorStrategy:
    """Generate multiple selector strategies with fallbacks"""
    
    def get_strategies(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Generate multiple selector strategies with fallbacks.
        Returns list of selectors to try in order - if first fails, try next.
        IWA uses dynamic environments (D1-D4), so we need multiple strategies.
        """
        prompt_lower = prompt.lower()
        strategies = []
        
        # Calendar view selectors - multiple strategies
        if "month" in prompt_lower or "month view" in prompt_lower:
            # Strategy 1: Exact text "Month" (most common)
            strategies.append(create_selector("tagContainsSelector", "Month", case_sensitive=False))
            # Strategy 2: Try "Monthly" (alternative text)
            strategies.append(create_selector("tagContainsSelector", "Monthly", case_sensitive=False))
            # Strategy 3: Try "Month View" (full phrase)
            strategies.append(create_selector("tagContainsSelector", "Month View", case_sensitive=False))
            # Strategy 4: Try attribute selectors (data-testid, aria-label)
            strategies.append(create_selector("attributeValueSelector", "month", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "month", attribute="aria-label", case_sensitive=False))
            # Strategy 5: Generic button fallback
            strategies.append(create_selector("attributeValueSelector", "button", attribute="custom", case_sensitive=False))
            return strategies
        
        if "week" in prompt_lower or "week view" in prompt_lower:
            # Strategy 1: Exact text "Week"
            strategies.append(create_selector("tagContainsSelector", "Week", case_sensitive=False))
            # Strategy 2: Try "Weekly"
            strategies.append(create_selector("tagContainsSelector", "Weekly", case_sensitive=False))
            # Strategy 3: Try "Week View"
            strategies.append(create_selector("tagContainsSelector", "Week View", case_sensitive=False))
            # Strategy 4: Attribute selectors
            strategies.append(create_selector("attributeValueSelector", "week", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "week", attribute="aria-label", case_sensitive=False))
            # Strategy 5: Generic fallback
            strategies.append(create_selector("attributeValueSelector", "button", attribute="custom", case_sensitive=False))
            return strategies
        
        if "day" in prompt_lower or "day view" in prompt_lower:
            strategies.append(create_selector("tagContainsSelector", "Day", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Daily", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Day View", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "day", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "button", attribute="custom", case_sensitive=False))
            return strategies
        
        # Generic click targets - improved strategy
        keywords = extract_keywords(prompt)
        
        # Priority words with multiple variations
        priority_words = {
            "month": ["Month", "Monthly", "Month View"],
            "week": ["Week", "Weekly", "Week View"],
            "day": ["Day", "Daily", "Day View"],
            "year": ["Year", "Yearly", "Year View"],
            "view": ["View", "Views"],
            "login": ["Login", "Sign In", "Log In"],
            "submit": ["Submit", "Save", "Send"],
            "search": ["Search", "Find"],
            "profile": ["Profile", "Account", "Settings"],
        }
        
        for word, variations in priority_words.items():
            if word in prompt_lower:
                for variation in variations:
                    strategies.append(create_selector("tagContainsSelector", variation, case_sensitive=False))
                # Also try attribute selectors
                strategies.append(create_selector("attributeValueSelector", word, attribute="data-testid", case_sensitive=False))
                strategies.append(create_selector("attributeValueSelector", word, attribute="aria-label", case_sensitive=False))
                break
        
        # Try target keywords with variations
        if keywords["targets"]:
            target = keywords["targets"][0]
            # Try capitalized versions
            strategies.append(create_selector("tagContainsSelector", target.title(), case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", target.upper(), case_sensitive=False))
            # Try as attribute
            strategies.append(create_selector("attributeValueSelector", target.lower(), attribute="name", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", target.lower(), attribute="id", case_sensitive=False))
        
        # Try action keywords
        if keywords["actions"]:
            action = keywords["actions"][0]
            strategies.append(create_selector("tagContainsSelector", action.title(), case_sensitive=False))
        
        # Common form field selectors
        form_fields = ["username", "password", "email", "name", "submit", "button"]
        for field in form_fields:
            if field in prompt_lower:
                strategies.append(create_selector("attributeValueSelector", field, attribute="name", case_sensitive=False))
                strategies.append(create_selector("attributeValueSelector", field, attribute="type", case_sensitive=False))
                strategies.append(create_selector("attributeValueSelector", field, attribute="id", case_sensitive=False))
        
        # Fallback: generic button/link selectors
        if not strategies:
            strategies.append(create_selector("tagContainsSelector", "button", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "button", attribute="type", case_sensitive=False))
        
        return strategies

