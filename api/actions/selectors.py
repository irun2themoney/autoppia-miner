"""Selector creation and strategies"""
from typing import Dict, Any, List
from ..utils.keywords import extract_keywords


def create_selector(
    selector_type: str,
    value: str,
    attribute: str = None,
    case_sensitive: bool = False
) -> Dict[str, Any]:
    """Create IWA selector object - Returns Autoppia framework format"""
    # Autoppia framework expects Selector objects with type, value, attribute fields
    # Format: {"type": "selectorType", "value": "...", "attribute": "...", "case_sensitive": false}

    if selector_type == "attributeValueSelector":
        if attribute:
            return {
                "type": "attributeValueSelector",
                "attribute": attribute,
                "value": value,
                "case_sensitive": case_sensitive
            }
        else:
            # Fallback to tagContainsSelector if no attribute
            return {
                "type": "tagContainsSelector",
                "value": value,
                "case_sensitive": case_sensitive
            }
    elif selector_type == "tagContainsSelector":
        return {
            "type": "tagContainsSelector",
            "value": value,
            "case_sensitive": case_sensitive
        }
    elif selector_type == "xpathSelector":
        return {
            "type": "xpathSelector",
            "value": value,
            "case_sensitive": case_sensitive
        }
    else:
        # Default to tagContainsSelector for unknown types
        return {
            "type": "tagContainsSelector",
            "value": value,
            "case_sensitive": case_sensitive
        }


class SelectorStrategy:
    """Generate multiple selector strategies with fallbacks"""
    
    def get_strategies(self, element_type: str, value: str = "") -> List[Dict[str, Any]]:
        """
        Generate multiple selector strategies with fallbacks.
        Returns list of selectors to try in order - if first fails, try next.
        IWA uses dynamic environments (D1-D4), so we need multiple strategies.
        
        Args:
            element_type: Type of element (month_view, file_input, tab, etc.)
            value: Optional value to match (e.g., tab name, button text)
        """
        element_lower = element_type.lower()
        value_lower = value.lower() if value else ""
        strategies = []
        
        # New pattern-specific selectors
        if element_lower == "month_view":
            strategies.append(create_selector("tagContainsSelector", "Month", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Month View", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "month", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "month", attribute="aria-label", case_sensitive=False))
            return strategies
        
        if element_lower == "file_input":
            strategies.append(create_selector("attributeValueSelector", "file", attribute="type", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "file", attribute="name", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Choose File", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Upload", case_sensitive=False))
            return strategies
        
        if element_lower == "create_event":
            strategies.append(create_selector("tagContainsSelector", value or "Create Event", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "New Event", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "create", attribute="data-testid", case_sensitive=False))
            return strategies
        
        if element_lower == "date":
            if value:
                strategies.append(create_selector("tagContainsSelector", value, case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "date", attribute="type", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "date", attribute="class", case_sensitive=False))
            return strategies
        
        if element_lower == "tab":
            if value:
                strategies.append(create_selector("tagContainsSelector", value.title(), case_sensitive=False))
                strategies.append(create_selector("attributeValueSelector", value.lower(), attribute="data-tab", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "tab", attribute="role", case_sensitive=False))
            return strategies
        
        if element_lower == "next_page":
            strategies.append(create_selector("tagContainsSelector", "Next", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", ">", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "next", attribute="aria-label", case_sensitive=False))
            return strategies
        
        if element_lower == "previous_page":
            strategies.append(create_selector("tagContainsSelector", "Previous", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "<", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "prev", attribute="aria-label", case_sensitive=False))
            return strategies
        
        if element_lower == "page_number":
            if value:
                strategies.append(create_selector("tagContainsSelector", value, case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "page", attribute="class", case_sensitive=False))
            return strategies
        
        if element_lower == "confirm":
            strategies.append(create_selector("tagContainsSelector", value or "Confirm", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "OK", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Accept", case_sensitive=False))
            return strategies
        
        if element_lower == "cancel":
            strategies.append(create_selector("tagContainsSelector", value or "Cancel", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "cancel", attribute="class", case_sensitive=False))
            return strategies
        
        # Job-specific selectors (Enhanced for AutoConnect - Tok's weak point)
        if element_lower == "job_search":
            strategies.append(create_selector("attributeValueSelector", "search", attribute="type", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "search", attribute="name", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "job-search", attribute="id", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "job-search", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "search", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "job", case_sensitive=False))
            return strategies
        
        if element_lower == "job_card":
            strategies.append(create_selector("attributeValueSelector", "job-card", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "job-listing", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "job-item", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "job", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "job", attribute="data-job-id", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "job", case_sensitive=False))
            return strategies
        
        if element_lower == "apply_button":
            strategies.append(create_selector("tagContainsSelector", "Apply", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Apply Now", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "apply", attribute="data-action", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "apply-button", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "apply", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "apply", case_sensitive=False))
            return strategies
        
        # AutoList-specific selectors (Tok's weak point - 50%)
        if element_lower == "add_item" or element_lower == "add_button":
            strategies.append(create_selector("tagContainsSelector", "Add", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "New Item", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Add Item", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "add", attribute="data-action", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "add-item", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "add", attribute="aria-label", case_sensitive=False))
            return strategies
        
        if element_lower == "list_item":
            strategies.append(create_selector("attributeValueSelector", "list-item", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "item", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "item", attribute="data-item", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "list-item", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("tagSelector", "li"))
            return strategies
        
        # AutoMail-specific selectors (Tok's weak point - 50%)
        if element_lower == "compose_button":
            strategies.append(create_selector("tagContainsSelector", "Compose", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "New Email", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "New Message", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "compose", attribute="data-action", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "compose", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "compose", attribute="aria-label", case_sensitive=False))
            return strategies
        
        if element_lower == "send_button":
            strategies.append(create_selector("tagContainsSelector", "Send", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "send", attribute="data-action", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "send", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "send", attribute="type", case_sensitive=False))
            return strategies
        
        if element_lower == "email_list" or element_lower == "email_item":
            strategies.append(create_selector("attributeValueSelector", "email-list", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "email-item", attribute="class", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "email", attribute="data-email", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "email-item", attribute="data-testid", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "email", case_sensitive=False))
            return strategies
        
        # Fallback to original prompt-based logic
        prompt_lower = element_type.lower()
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
        # Handle common button clicks first
        if "button" in prompt_lower or element_lower in ["click", "press"]:
            # For generic button clicks, try multiple common selectors
            strategies.append(create_selector("cssSelector", "button, input[type='submit'], input[type='button'], [role='button']"))
            strategies.append(create_selector("tagContainsSelector", "Button", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "Submit", case_sensitive=False))
            strategies.append(create_selector("tagContainsSelector", "OK", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "button", attribute="type", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "submit", attribute="type", case_sensitive=False))
            return strategies

        # Use element_type as prompt for keyword extraction
        prompt_for_keywords = element_type if not value else f"{element_type} {value}"
        keywords = extract_keywords(prompt_for_keywords)
        
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
                # Try data attributes
                strategies.append(create_selector("attributeValueSelector", field, attribute="data-testid", case_sensitive=False))
                strategies.append(create_selector("attributeValueSelector", field, attribute="data-cy", case_sensitive=False))
        
        # XPath fallbacks for complex cases
        if keywords["targets"]:
            target = keywords["targets"][0].lower()
            # Generate XPath selectors as last resort
            xpath_strategies = [
                f"//button[contains(text(), '{target.title()}')]",
                f"//a[contains(text(), '{target.title()}')]",
                f"//*[@class='{target}']",
                f"//*[@id='{target}']",
            ]
            for xpath in xpath_strategies[:2]:  # Limit to 2 XPath selectors
                strategies.append(create_selector("xpathSelector", xpath, case_sensitive=False))
        
        # Fallback: generic button/link selectors
        if not strategies:
            strategies.append(create_selector("tagContainsSelector", "button", case_sensitive=False))
            strategies.append(create_selector("attributeValueSelector", "button", attribute="type", case_sensitive=False))
            # Last resort XPath
            strategies.append(create_selector("xpathSelector", "//button[1]", case_sensitive=False))
        
        return strategies

