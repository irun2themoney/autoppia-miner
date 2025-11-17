"""Advanced visual and contextual selector strategies"""
from typing import Dict, Any, List, Optional
import re


class VisualSelectorGenerator:
    """Generate advanced visual and contextual selectors"""
    
    # Visual position hints
    POSITION_HINTS = {
        "top": ["top", "header", "nav", "menu"],
        "bottom": ["bottom", "footer", "end"],
        "left": ["left", "sidebar", "side"],
        "right": ["right", "sidebar", "side"],
        "center": ["center", "middle", "main"],
    }
    
    # Size hints
    SIZE_HINTS = {
        "large": ["large", "big", "main", "primary"],
        "small": ["small", "tiny", "mini"],
        "wide": ["wide", "full", "expanded"],
    }
    
    # Color hints (for buttons)
    COLOR_HINTS = {
        "primary": ["primary", "blue", "main", "important"],
        "secondary": ["secondary", "gray", "grey"],
        "success": ["success", "green", "ok", "confirm"],
        "danger": ["danger", "red", "delete", "remove", "cancel"],
        "warning": ["warning", "yellow", "orange", "caution"],
    }
    
    def generate_contextual_selectors(self, prompt: str, element_type: str = "button") -> List[Dict[str, Any]]:
        """Generate selectors based on visual and contextual hints"""
        selectors = []
        prompt_lower = prompt.lower()
        
        # Extract position hints
        for position, keywords in self.POSITION_HINTS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                # Generate position-based XPath
                if position == "top":
                    selectors.append({
                        "type": "xpathSelector",
                        "value": f"//{element_type}[position()=1]",
                        "case_sensitive": False
                    })
                elif position == "bottom":
                    selectors.append({
                        "type": "xpathSelector",
                        "value": f"//{element_type}[position()=last()]",
                        "case_sensitive": False
                    })
        
        # Extract size hints
        for size, keywords in self.SIZE_HINTS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if size == "large":
                    # Look for buttons with large classes or styles
                    selectors.append({
                        "type": "xpathSelector",
                        "value": f"//{element_type}[contains(@class, 'large') or contains(@class, 'big') or contains(@class, 'primary')]",
                        "case_sensitive": False
                    })
        
        # Extract color hints
        for color, keywords in self.COLOR_HINTS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                selectors.append({
                    "type": "xpathSelector",
                    "value": f"//{element_type}[contains(@class, '{color}') or contains(@class, 'btn-{color}')]",
                    "case_sensitive": False
                })
        
        return selectors
    
    def generate_semantic_selectors(self, prompt: str, target_text: str) -> List[Dict[str, Any]]:
        """Generate semantic selectors based on meaning"""
        selectors = []
        prompt_lower = prompt.lower()
        target_lower = target_text.lower()
        
        # Common semantic mappings
        semantic_map = {
            "submit": ["submit", "send", "save", "confirm", "ok", "done", "finish"],
            "cancel": ["cancel", "close", "back", "exit", "abort"],
            "delete": ["delete", "remove", "trash", "clear"],
            "edit": ["edit", "modify", "change", "update"],
            "add": ["add", "create", "new", "insert"],
            "search": ["search", "find", "look", "query"],
        }
        
        # Find semantic matches
        for semantic, keywords in semantic_map.items():
            if any(keyword in prompt_lower or keyword in target_lower for keyword in keywords):
                # Generate semantic-based selectors
                selectors.append({
                    "type": "attributeValueSelector",
                    "value": semantic,
                    "attribute": "data-action",
                    "case_sensitive": False
                })
                selectors.append({
                    "type": "attributeValueSelector",
                    "value": semantic,
                    "attribute": "aria-label",
                    "case_sensitive": False
                })
                selectors.append({
                    "type": "xpathSelector",
                    "value": f"//*[@data-action='{semantic}' or contains(@aria-label, '{semantic}')]",
                    "case_sensitive": False
                })
        
        return selectors
    
    def generate_priority_selectors(self, target_text: str, element_type: str = "button") -> List[Dict[str, Any]]:
        """Generate priority-ordered selectors for maximum success"""
        selectors = []
        
        # 1. Exact text match (highest priority)
        selectors.append({
            "type": "tagContainsSelector",
            "value": target_text,
            "case_sensitive": False
        })
        
        # 2. Data attributes (high priority - often used for testing)
        selectors.append({
            "type": "attributeValueSelector",
            "value": target_text.lower().replace(" ", "-"),
            "attribute": "data-testid",
            "case_sensitive": False
        })
        selectors.append({
            "type": "attributeValueSelector",
            "value": target_text.lower().replace(" ", "-"),
            "attribute": "data-cy",
            "case_sensitive": False
        })
        
        # 3. ID attribute
        selectors.append({
            "type": "attributeValueSelector",
            "value": target_text.lower().replace(" ", "-"),
            "attribute": "id",
            "case_sensitive": False
        })
        
        # 4. Aria-label
        selectors.append({
            "type": "attributeValueSelector",
            "value": target_text,
            "attribute": "aria-label",
            "case_sensitive": False
        })
        
        # 5. Class name (contains)
        selectors.append({
            "type": "xpathSelector",
            "value": f"//{element_type}[contains(@class, '{target_text.lower().replace(' ', '-')}')]",
            "case_sensitive": False
        })
        
        # 6. XPath with text contains
        selectors.append({
            "type": "xpathSelector",
            "value": f"//{element_type}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_text.lower()}')]",
            "case_sensitive": False
        })
        
        # 7. XPath with any text node
        selectors.append({
            "type": "xpathSelector",
            "value": f"//{element_type}[.//text()[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{target_text.lower()}')]]",
            "case_sensitive": False
        })
        
        return selectors
    
    def enhance_with_context(self, base_selectors: List[Dict[str, Any]], prompt: str, url: str) -> List[Dict[str, Any]]:
        """Enhance selectors with contextual information"""
        enhanced = base_selectors.copy()
        
        # Add visual selectors
        visual = self.generate_contextual_selectors(prompt)
        enhanced.extend(visual)
        
        # Add semantic selectors for each base selector
        for selector in base_selectors[:3]:  # Only for first 3 to avoid too many
            if selector.get("type") == "tagContainsSelector":
                semantic = self.generate_semantic_selectors(prompt, selector.get("value", ""))
                enhanced.extend(semantic)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_selectors = []
        for s in enhanced:
            key = (s.get("type"), s.get("value"), s.get("attribute", ""))
            if key not in seen:
                seen.add(key)
                unique_selectors.append(s)
        
        return unique_selectors[:10]  # Limit to 10 selectors

