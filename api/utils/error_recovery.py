"""Error recovery and retry logic"""
from typing import Dict, Any, List, Optional, Callable
import asyncio
import logging


class ErrorRecovery:
    """Handle errors and retry with alternative strategies"""
    
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
    
    async def retry_with_fallback(
        self,
        primary_func: Callable,
        fallback_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Try primary function, fallback on error"""
        for attempt in range(self.max_retries + 1):
            try:
                result = await primary_func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                if attempt < self.max_retries:
                    logging.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logging.warning(f"All attempts failed, using fallback: {e}")
        
        # Try fallback
        try:
            return await fallback_func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Fallback also failed: {e}")
            raise
    
    def get_alternative_selectors(self, selector: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative selectors if primary fails"""
        alternatives = []
        selector_type = selector.get("type", "")
        value = selector.get("value", "")
        
        if selector_type == "tagContainsSelector":
            # Try attribute selectors
            alternatives.append({
                "type": "attributeValueSelector",
                "value": value.lower(),
                "attribute": "data-testid",
                "case_sensitive": False
            })
            alternatives.append({
                "type": "attributeValueSelector",
                "value": value.lower(),
                "attribute": "aria-label",
                "case_sensitive": False
            })
            # Try XPath
            alternatives.append({
                "type": "xpathSelector",
                "value": f"//*[contains(text(), '{value}')]",
                "case_sensitive": False
            })
        
        elif selector_type == "attributeValueSelector":
            # Try tagContainsSelector
            alternatives.append({
                "type": "tagContainsSelector",
                "value": value,
                "case_sensitive": False
            })
            # Try different attributes
            current_attr = selector.get("attribute", "")
            other_attrs = ["id", "name", "class", "data-testid", "aria-label"]
            for attr in other_attrs:
                if attr != current_attr:
                    alternatives.append({
                        "type": "attributeValueSelector",
                        "value": value,
                        "attribute": attr,
                        "case_sensitive": False
                    })
        
        return alternatives

