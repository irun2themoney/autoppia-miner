"""Enhanced selector strategies with visual and semantic hints"""
from typing import Dict, Any, List
import re


class SelectorEnhancer:
    """Enhance selectors with better strategies"""
    
    # Common button text variations
    BUTTON_VARIANTS = {
        "login": ["Login", "Sign In", "Log In", "Sign in", "Log in", "LOGIN"],
        "submit": ["Submit", "Send", "Save", "Confirm", "OK", "Done"],
        "search": ["Search", "Find", "Go", "Submit"],
        "cancel": ["Cancel", "Close", "Back", "Exit"],
        "next": ["Next", "Continue", "Forward", ">"],
        "previous": ["Previous", "Back", "<", "←"],
    }
    
    # Common form field patterns
    FORM_FIELD_PATTERNS = {
        "username": ["username", "user", "login", "email", "account"],
        "password": ["password", "pass", "pwd", "secret"],
        "email": ["email", "e-mail", "mail", "email address"],
        "name": ["name", "full name", "first name", "last name"],
        "phone": ["phone", "telephone", "mobile", "cell"],
        "address": ["address", "street", "location"],
    }
    
    def enhance_selector(self, selector: Dict[str, Any], prompt: str, action_type: str) -> List[Dict[str, Any]]:
        """Enhance a selector with multiple strategies"""
        strategies = [selector]  # Start with original
        
        selector_type = selector.get("type", "")
        value = selector.get("value", "").lower()
        prompt_lower = prompt.lower()
        
        if selector_type == "tagContainsSelector":
            # Add variations
            if value in self.BUTTON_VARIANTS:
                for variant in self.BUTTON_VARIANTS[value]:
                    strategies.append({
                        "type": "tagContainsSelector",
                        "value": variant,
                        "case_sensitive": False
                    })
            
            # Add attribute selectors
            strategies.append({
                "type": "attributeValueSelector",
                "value": value,
                "attribute": "data-testid",
                "case_sensitive": False
            })
            strategies.append({
                "type": "attributeValueSelector",
                "value": value,
                "attribute": "aria-label",
                "case_sensitive": False
            })
            strategies.append({
                "type": "attributeValueSelector",
                "value": value,
                "attribute": "id",
                "case_sensitive": False
            })
            
            # Add XPath as last resort
            strategies.append({
                "type": "xpathSelector",
                "value": f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{value}')]",
                "case_sensitive": False
            })
            strategies.append({
                "type": "xpathSelector",
                "value": f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{value}')]",
                "case_sensitive": False
            })
        
        elif selector_type == "attributeValueSelector":
            # Try other attributes
            current_attr = selector.get("attribute", "")
            other_attrs = ["id", "name", "class", "data-testid", "aria-label", "placeholder", "type"]
            
            for attr in other_attrs:
                if attr != current_attr:
                    strategies.append({
                        "type": "attributeValueSelector",
                        "value": value,
                        "attribute": attr,
                        "case_sensitive": False
                    })
            
            # Try tagContainsSelector
            strategies.append({
                "type": "tagContainsSelector",
                "value": value,
                "case_sensitive": False
            })
        
        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_strategies = []
        for s in strategies:
            key = (s.get("type"), s.get("value"), s.get("attribute", ""))
            if key not in seen:
                seen.add(key)
                unique_strategies.append(s)
        
        return unique_strategies[:8]  # Limit to 8 strategies
    
    def get_form_field_selectors(self, field_type: str) -> List[Dict[str, Any]]:
        """Get selectors for form fields"""
        if field_type not in self.FORM_FIELD_PATTERNS:
            return []
        
        patterns = self.FORM_FIELD_PATTERNS[field_type]
        selectors = []
        
        for pattern in patterns:
            # Try name attribute
            selectors.append({
                "type": "attributeValueSelector",
                "value": pattern,
                "attribute": "name",
                "case_sensitive": False
            })
            # Try id attribute
            selectors.append({
                "type": "attributeValueSelector",
                "value": pattern,
                "attribute": "id",
                "case_sensitive": False
            })
            # Try placeholder
            selectors.append({
                "type": "attributeValueSelector",
                "value": pattern,
                "attribute": "placeholder",
                "case_sensitive": False
            })
            # Try type attribute (for password, email)
            if field_type in ["password", "email"]:
                selectors.append({
                    "type": "attributeValueSelector",
                    "value": field_type,
                    "attribute": "type",
                    "case_sensitive": False
                })
        
        return selectors[:6]  # Limit to 6 selectors

