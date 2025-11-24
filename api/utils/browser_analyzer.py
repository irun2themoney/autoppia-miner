"""Browser automation using Playwright for accurate selector generation"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

# Global browser instance (singleton)
_browser: Optional[Browser] = None
_playwright = None
PLAYWRIGHT_AVAILABLE = True  # Assume available if module imports


class BrowserAnalyzer:
    """Analyze web pages using Playwright to generate accurate selectors"""
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    async def fetch_page(self, url: str, timeout: float = 15.0) -> Optional[Dict[str, Any]]:
        """
        Fetch page with full browser automation
        
        Returns:
            Dict with 'html', 'url', 'title', 'elements' or None if failed
        """
        try:
            page = await self.browser.new_page()
            
            # Set reasonable timeouts
            page.set_default_timeout(timeout * 1000)  # Convert to ms
            
            try:
                # Navigate to page
                response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                
                if not response or response.status >= 400:
                    logger.warning(f"Page returned status {response.status if response else 'None'} for {url}")
                    await page.close()
                    return None
                
                # OPTIMIZED: Use domcontentloaded instead of networkidle for faster loading
                # networkidle waits for all network activity to stop (slower)
                # domcontentloaded is faster and sufficient for most cases
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=3000)
                except:
                    # Fallback: just wait a bit if domcontentloaded fails
                    await asyncio.sleep(0.5)
                
                # Get page data
                html = await page.content()
                title = await page.title()
                final_url = page.url
                
                # Extract key elements (forms, buttons, inputs)
                elements = await self._extract_elements(page)
                
                await page.close()
                
                return {
                    "html": html,
                    "url": final_url,
                    "title": title,
                    "elements": elements
                }
                
            except PlaywrightTimeoutError:
                logger.warning(f"Timeout loading page {url}")
                await page.close()
                return None
            except Exception as e:
                logger.error(f"Error loading page {url}: {e}")
                await page.close()
                return None
                
        except Exception as e:
            logger.error(f"Error creating page for {url}: {e}")
            return None
    
    async def _extract_elements(self, page: Page) -> List[Dict[str, Any]]:
        """Extract key interactive elements from page"""
        elements = []
        
        try:
            # Extract buttons (including more variations)
            buttons = await page.query_selector_all("button, input[type='submit'], input[type='button'], a[role='button'], [onclick], .btn, [class*='button']")
            for btn in buttons[:30]:  # Limit to first 30
                try:
                    text = await btn.inner_text()
                    btn_type = await btn.get_attribute("type") or "button"
                    btn_id = await btn.get_attribute("id")
                    btn_name = await btn.get_attribute("name")
                    btn_class = await btn.get_attribute("class")
                    data_testid = await btn.get_attribute("data-testid")
                    aria_label = await btn.get_attribute("aria-label")
                    data_action = await btn.get_attribute("data-action")
                    value = await btn.get_attribute("value")
                    
                    elements.append({
                        "type": "button",
                        "tag": "button",
                        "text": text.strip() if text else (value or ""),
                        "id": btn_id,
                        "name": btn_name,
                        "class": btn_class,
                        "data-testid": data_testid,
                        "data-action": data_action,
                        "aria-label": aria_label,
                        "aria-label": aria_label,
                        "selector": await self._generate_selector(btn, text)
                    })
                except Exception as e:
                    logger.debug(f"Error extracting button: {e}")
                    continue
            
            # Extract form inputs
            inputs = await page.query_selector_all("input, textarea, select")
            for inp in inputs[:30]:  # Limit to first 30
                try:
                    inp_type = await inp.get_attribute("type") or "text"
                    inp_id = await inp.get_attribute("id")
                    inp_name = await inp.get_attribute("name")
                    inp_placeholder = await inp.get_attribute("placeholder")
                    inp_class = await inp.get_attribute("class")
                    data_testid = await inp.get_attribute("data-testid")
                    
                    # Determine field type
                    field_type = "text"
                    if inp_type in ["email", "password", "username", "text"]:
                        field_type = inp_type
                    elif inp_name:
                        if "user" in inp_name.lower() or "login" in inp_name.lower():
                            field_type = "username"
                        elif "pass" in inp_name.lower():
                            field_type = "password"
                        elif "email" in inp_name.lower() or "mail" in inp_name.lower():
                            field_type = "email"
                    
                    elements.append({
                        "type": field_type,
                        "tag": "input",
                        "input_type": inp_type,
                        "id": inp_id,
                        "name": inp_name,
                        "placeholder": inp_placeholder,
                        "class": inp_class,
                        "data-testid": data_testid,
                        "selector": await self._generate_selector(inp, None)
                    })
                except Exception as e:
                    logger.debug(f"Error extracting input: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting elements: {e}")
        
        return elements
    
    async def _generate_selector(self, element, text: Optional[str] = None) -> str:
        """Generate CSS selector for element"""
        try:
            # Try ID first (most specific)
            element_id = await element.get_attribute("id")
            if element_id:
                return f"#{element_id}"
            
            # Try data-testid
            data_testid = await element.get_attribute("data-testid")
            if data_testid:
                return f"[data-testid='{data_testid}']"
            
            # Try name
            name = await element.get_attribute("name")
            if name:
                return f"[name='{name}']"
            
            # Try class
            class_name = await element.get_attribute("class")
            if class_name:
                # Use first class
                first_class = class_name.split()[0] if class_name else None
                if first_class:
                    return f".{first_class}"
            
            # Fallback to tag
            tag = await element.evaluate("el => el.tagName.toLowerCase()")
            return tag
            
        except Exception as e:
            logger.debug(f"Error generating selector: {e}")
            return "button"  # Fallback
    
    def analyze_dom(self, page_data: Dict[str, Any], intent: str, task_type: str) -> List[Dict[str, Any]]:
        """
        Analyze DOM and generate selectors based on intent
        
        Args:
            page_data: Page data from fetch_page
            intent: User intent (prompt)
            task_type: Type of task (login, register, etc.)
        
        Returns:
            List of selector candidates with confidence scores (IWA format)
        """
        if not page_data or "elements" not in page_data:
            return []
        
        # Import here to avoid circular dependency
        from ..actions.selectors import create_selector
        
        intent_lower = intent.lower()
        elements = page_data.get("elements", [])
        candidates = []
        
        # Match elements to intent
        for elem in elements:
            confidence = 0.0
            css_selector = elem.get("selector", "")  # CSS selector string from _generate_selector
            
            # Convert CSS selector to IWA format
            iwa_selector = self._css_to_iwa_selector(css_selector, elem)
            
            # Login/Register tasks
            if task_type in ["login", "register"] or "login" in intent_lower or "register" in intent_lower:
                if elem.get("type") == "username":
                    confidence = 0.9
                elif elem.get("type") == "password":
                    confidence = 0.9
                elif elem.get("type") == "email":
                    confidence = 0.8
                elif "submit" in elem.get("text", "").lower() or "login" in elem.get("text", "").lower() or "register" in elem.get("text", "").lower():
                    confidence = 0.8
            
            # Click tasks
            elif "click" in intent_lower:
                text = elem.get("text", "").lower()
                # Check for specific button text matches
                if any(word in text for word in ["button", "submit", "ok", "save", "send", "next", "continue", "apply"]):
                    confidence = 0.9
                elif any(word in text for word in intent_lower.split() if len(word) > 3):
                    confidence = 0.8
                elif elem.get("type") == "button" or elem.get("tag") == "button":
                    confidence = 0.6  # Any button is a reasonable match for "click"
            
            # Type tasks
            elif "type" in intent_lower or "enter" in intent_lower or "fill" in intent_lower:
                if elem.get("type") in ["text", "email", "username", "password"]:
                    confidence = 0.7
            
            # Submit tasks
            elif "submit" in intent_lower:
                if elem.get("type") == "button" and ("submit" in elem.get("text", "").lower() or elem.get("input_type") == "submit"):
                    confidence = 0.9
            
            if confidence > 0.4:  # Only return candidates with reasonable confidence
                candidates.append({
                    "selector": iwa_selector,  # IWA format selector
                    "type": elem.get("type", "unknown"),
                    "confidence": confidence,
                    "element": elem
                })
        
        # Sort by confidence
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        
        return candidates[:10]  # Return top 10 candidates
    
    def _css_to_iwa_selector(self, css_selector: str, elem: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CSS selector string to IWA format"""
        from ..actions.selectors import create_selector
        
        if not css_selector:
            # Fallback: try to build from element attributes
            if elem.get("id"):
                return create_selector("attributeValueSelector", elem["id"], attribute="id")
            elif elem.get("data-testid"):
                return create_selector("attributeValueSelector", elem["data-testid"], attribute="data-testid")
            elif elem.get("name"):
                return create_selector("attributeValueSelector", elem["name"], attribute="name")
            else:
                return create_selector("tagContainsSelector", "button", case_sensitive=False)
        
        # Convert CSS selector to IWA format
        if css_selector.startswith("#"):
            # ID selector: #myId -> attributeValueSelector with id
            return create_selector("attributeValueSelector", css_selector[1:], attribute="id")
        elif css_selector.startswith("."):
            # Class selector: .myClass -> tagContainsSelector
            return create_selector("tagContainsSelector", css_selector[1:], case_sensitive=False)
        elif css_selector.startswith("[") and "=" in css_selector:
            # Attribute selector: [name='value'] -> attributeValueSelector
            import re
            match = re.search(r'\[([^\]]+)=["\']([^"\']+)["\']\]', css_selector)
            if match:
                attr_name, attr_value = match.groups()
                return create_selector("attributeValueSelector", attr_value, attribute=attr_name)
            else:
                return create_selector("tagContainsSelector", css_selector, case_sensitive=False)
        else:
            # Generic tag or text -> tagContainsSelector
            return create_selector("tagContainsSelector", css_selector, case_sensitive=False)


# Singleton browser instance
async def _get_browser() -> Optional[Browser]:
    """Get or create browser instance"""
    global _browser, _playwright
    
    if _browser is None:
        try:
            _playwright = await async_playwright().start()
            _browser = await _playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']  # For server environments
            )
            logger.info("✅ Playwright browser launched")
        except Exception as e:
            logger.error(f"❌ Failed to launch Playwright browser: {e}")
            return None
    
    return _browser


async def get_browser_analyzer() -> Optional[BrowserAnalyzer]:
    """Get browser analyzer instance"""
    try:
        browser = await _get_browser()
        if browser:
            return BrowserAnalyzer(browser)
        return None
    except Exception as e:
        logger.error(f"Failed to get browser analyzer: {e}")
        return None


async def close_browser():
    """Close browser instance (cleanup)"""
    global _browser, _playwright
    
    if _browser:
        try:
            await _browser.close()
            _browser = None
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    if _playwright:
        try:
            await _playwright.stop()
            _playwright = None
        except Exception as e:
            logger.error(f"Error stopping playwright: {e}")

