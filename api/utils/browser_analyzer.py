"""
Browser Automation Module using Playwright
Fetches real page content with JavaScript execution and generates verified selectors.
This is a significant upgrade from basic HTTP fetching - handles dynamic content!
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Try to import Playwright - graceful fallback if not installed
try:
    from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Install with: pip install playwright && playwright install chromium")


class PlaywrightBrowserAnalyzer:
    """
    Advanced browser automation analyzer using Playwright.
    Handles JavaScript-rendered pages and generates accurate selectors.
    """
    
    def __init__(self, timeout: float = 15.0, headless: bool = True):
        """
        Initialize browser analyzer.
        
        Args:
            timeout: Maximum time to wait for page load (seconds)
            headless: Run browser in headless mode (faster, less resource-intensive)
        """
        self.timeout = timeout * 1000  # Playwright uses milliseconds
        self.headless = headless
        self.browser: Optional[Browser] = None
        self._browser_context = None
        self._playwright = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        if PLAYWRIGHT_AVAILABLE:
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']  # Required for Docker/servers
            )
            self._browser_context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup"""
        if self._browser_context:
            await self._browser_context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()
    
    async def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch page with full browser automation.
        Returns dict with HTML, DOM snapshot, and metadata.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dict with keys: 'html', 'dom_snapshot', 'screenshot' (optional), 'metadata'
            None if fetch fails
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, cannot fetch page")
            return None
            
        if not url or not url.startswith("http"):
            return None
        
        try:
            page = await self._browser_context.new_page()
            
            # Navigate to page with timeout
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
                # Wait a bit for JavaScript to execute
                await page.wait_for_timeout(1000)  # 1 second for JS execution
            except PlaywrightTimeoutError:
                logger.warning(f"Page load timeout for {url}, using partial content")
                # Continue with whatever loaded
            
            # Get page content
            html = await page.content()
            
            # Get DOM snapshot (simplified representation)
            dom_snapshot = await self._get_dom_snapshot(page)
            
            # Get metadata
            metadata = {
                'url': url,
                'title': await page.title(),
                'viewport': page.viewport_size,
            }
            
            await page.close()
            
            return {
                'html': html,
                'dom_snapshot': dom_snapshot,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error fetching page with Playwright: {e}")
            return None
    
    async def _get_dom_snapshot(self, page: Page) -> Dict[str, Any]:
        """Get a simplified DOM snapshot for analysis"""
        try:
            # Execute JavaScript to get element information
            snapshot = await page.evaluate("""
                () => {
                    const elements = [];
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_ELEMENT,
                        null,
                        false
                    );
                    
                    let node;
                    while (node = walker.nextNode()) {
                        if (node.tagName && ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA'].includes(node.tagName)) {
                            elements.push({
                                tag: node.tagName,
                                id: node.id || null,
                                name: node.name || null,
                                type: node.type || null,
                                text: node.textContent?.trim().substring(0, 50) || '',
                                className: node.className || null,
                                href: node.href || null,
                                placeholder: node.placeholder || null,
                                value: node.value || null,
                                ariaLabel: node.getAttribute('aria-label') || null,
                                dataTestId: node.getAttribute('data-testid') || null,
                                visible: node.offsetWidth > 0 && node.offsetHeight > 0
                            });
                        }
                    }
                    return elements;
                }
            """)
            return {'interactive_elements': snapshot}
        except Exception as e:
            logger.warning(f"Error getting DOM snapshot: {e}")
            return {'interactive_elements': []}
    
    def analyze_dom(self, page_data: Dict[str, Any], intent: str, task_type: str = "generic") -> List[Dict[str, Any]]:
        """
        Analyze DOM and find elements matching the intent.
        Uses both HTML parsing and DOM snapshot for better accuracy.
        
        Args:
            page_data: Dict from fetch_page() with 'html' and 'dom_snapshot'
            intent: Task intent/prompt
            task_type: Type of task (login, form, etc.)
            
        Returns:
            List of potential selectors sorted by confidence
        """
        if not page_data or not page_data.get('html'):
            return []
        
        candidates = []
        
        # Strategy 1: Use DOM snapshot (faster, more accurate for interactive elements)
        if page_data.get('dom_snapshot', {}).get('interactive_elements'):
            candidates.extend(
                self._analyze_dom_snapshot(
                    page_data['dom_snapshot']['interactive_elements'],
                    intent,
                    task_type
                )
            )
        
        # Strategy 2: Use BeautifulSoup for HTML parsing (fallback, handles all elements)
        try:
            soup = BeautifulSoup(page_data['html'], "lxml")
            # Remove scripts and styles
            for script in soup(["script", "style", "meta", "noscript"]):
                script.decompose()
            
            if task_type == "login":
                candidates.extend(self._find_login_elements(soup, intent))
            elif task_type == "job_apply":
                candidates.extend(self._find_job_elements(soup, intent))
            else:
                candidates.extend(self._find_generic_elements(soup, intent))
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
        
        # Deduplicate and sort by confidence
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            selector_key = candidate.get('selector', {}).get('value', '') if isinstance(candidate.get('selector'), dict) else str(candidate.get('selector', ''))
            if selector_key and selector_key not in seen:
                seen.add(selector_key)
                unique_candidates.append(candidate)
        
        return sorted(unique_candidates, key=lambda x: x.get("confidence", 0), reverse=True)
    
    def _analyze_dom_snapshot(self, elements: List[Dict], intent: str, task_type: str) -> List[Dict[str, Any]]:
        """Analyze DOM snapshot for interactive elements"""
        candidates = []
        intent_lower = intent.lower()
        keywords = [k.strip().lower() for k in intent_lower.split() if len(k) > 3]
        
        for elem in elements:
            if not elem.get('visible', True):
                continue  # Skip invisible elements
            
            score = 0
            selector_candidates = []
            
            # Build selector candidates (prioritize stable selectors)
            if elem.get('id'):
                selector_candidates.append({
                    'selector': f"#{elem['id']}",
                    'confidence': 0.95,
                    'strategy': 'id'
                })
            
            if elem.get('dataTestId'):
                selector_candidates.append({
                    'selector': f'[data-testid="{elem["dataTestId"]}"]',
                    'confidence': 0.90,
                    'strategy': 'data_testid'
                })
            
            if elem.get('name'):
                selector_candidates.append({
                    'selector': f'{elem["tag"].lower()}[name="{elem["name"]}"]',
                    'confidence': 0.85,
                    'strategy': 'name'
                })
            
            if elem.get('ariaLabel'):
                selector_candidates.append({
                    'selector': f'[aria-label="{elem["ariaLabel"]}"]',
                    'confidence': 0.80,
                    'strategy': 'aria_label'
                })
            
            # Score based on text/attributes matching intent
            text = elem.get('text', '').lower()
            if text:
                for keyword in keywords:
                    if keyword in text:
                        score += 0.3
            
            if elem.get('placeholder'):
                placeholder = elem['placeholder'].lower()
                for keyword in keywords:
                    if keyword in placeholder:
                        score += 0.2
            
            if elem.get('ariaLabel'):
                aria = elem['ariaLabel'].lower()
                for keyword in keywords:
                    if keyword in aria:
                        score += 0.25
            
            # Task-specific scoring
            if task_type == "login":
                if elem.get('type') == 'password':
                    score += 0.5
                if any(term in text for term in ['login', 'sign in', 'submit']):
                    score += 0.4
            
            if score > 0.3 and selector_candidates:
                # Use best selector candidate
                best_selector = selector_candidates[0]
                candidates.append({
                    'selector': best_selector['selector'],
                    'confidence': min(best_selector['confidence'] + score, 1.0),
                    'type': elem.get('tag', 'unknown'),
                    'text': text[:30],
                    'strategy': best_selector['strategy']
                })
        
        return candidates
    
    def _find_login_elements(self, soup: BeautifulSoup, intent: str) -> List[Dict[str, Any]]:
        """Find login-related fields and buttons (from HTML parsing)"""
        selectors = []
        user_terms = ["user", "login", "email", "username"]
        pass_terms = ["pass", "pwd", "secret"]
        submit_terms = ["sign in", "log in", "submit", "enter"]
        
        for input_tag in soup.find_all("input"):
            attrs = input_tag.attrs
            score = 0
            field_type = "unknown"
            
            attr_str = " ".join([str(v) for v in attrs.values()]).lower()
            
            if any(t in attr_str for t in user_terms):
                score += 0.8
                field_type = "username"
            elif any(t in attr_str for t in pass_terms) or attrs.get("type") == "password":
                score += 0.9
                field_type = "password"
            elif attrs.get("type") in ["submit", "button"]:
                score += 0.5
                field_type = "submit"
            
            if score > 0.5:
                selector = self._generate_selector(input_tag)
                if selector:
                    selectors.append({
                        "selector": selector,
                        "type": field_type,
                        "confidence": score,
                        "tag": "input"
                    })
        
        for btn in soup.find_all(["button", "a"]):
            text = btn.get_text().strip().lower()
            if any(t in text for t in submit_terms):
                selector = self._generate_selector(btn)
                if selector:
                    selectors.append({
                        "selector": selector,
                        "type": "submit",
                        "confidence": 0.9,
                        "tag": btn.name
                    })
        
        return selectors
    
    def _find_job_elements(self, soup: BeautifulSoup, intent: str) -> List[Dict[str, Any]]:
        """Find job application elements"""
        selectors = []
        apply_terms = ["apply", "easy apply", "apply now", "start application"]
        
        for tag in soup.find_all(["button", "a", "div", "span"]):
            text = tag.get_text().strip().lower()
            
            if text in apply_terms:
                selector = self._generate_selector(tag)
                if selector:
                    selectors.append({
                        "selector": selector,
                        "type": "apply_button",
                        "confidence": 0.95,
                        "text": text
                    })
            elif any(t in text for t in apply_terms) and len(text) < 30:
                selector = self._generate_selector(tag)
                if selector:
                    selectors.append({
                        "selector": selector,
                        "type": "apply_button",
                        "confidence": 0.7,
                        "text": text
                    })
        
        return selectors
    
    def _find_generic_elements(self, soup: BeautifulSoup, intent: str) -> List[Dict[str, Any]]:
        """Find elements matching generic intent keywords"""
        selectors = []
        keywords = [k.strip().lower() for k in intent.split() if len(k) > 3]
        
        if not keywords:
            return []
        
        for tag in soup.find_all(["button", "a", "input", "div", "span"]):
            text = tag.get_text().strip().lower()
            attrs = str(tag.attrs).lower()
            
            score = 0
            matches = 0
            
            for k in keywords:
                if k in text:
                    score += 0.3
                    matches += 1
                if k in attrs:
                    score += 0.1
                    matches += 1
            
            if tag.name in ["button", "a", "input"]:
                score += 0.2
            
            if matches > 0 and score > 0.3:
                selector = self._generate_selector(tag)
                if selector:
                    selectors.append({
                        "selector": selector,
                        "confidence": min(score, 1.0),
                        "text": text[:20]
                    })
        
        return sorted(selectors, key=lambda x: x["confidence"], reverse=True)
    
    def _generate_selector(self, tag) -> Optional[str]:
        """Generate a robust CSS selector for a BeautifulSoup tag"""
        try:
            # Priority: ID > data-testid > name > class > tag
            if tag.has_attr("id"):
                id_val = tag["id"]
                if len(id_val) < 30 and not re.search(r'\d{5,}', id_val):
                    return f"#{id_val}"
            
            if tag.has_attr("data-testid"):
                return f'[data-testid="{tag["data-testid"]}"]'
            
            if tag.has_attr("name"):
                return f'{tag.name}[name="{tag["name"]}"]'
            
            if tag.has_attr("class") and tag["class"]:
                classes = [c for c in tag["class"] if c not in ["btn", "button", "active", "hidden"]]
                if classes:
                    return f".{classes[0]}"
            
            return tag.name
        except Exception:
            return tag.name if tag else "body"


# Global instance (will be initialized on first use)
_browser_analyzer: Optional[PlaywrightBrowserAnalyzer] = None


async def get_browser_analyzer() -> Optional[PlaywrightBrowserAnalyzer]:
    """Get or create browser analyzer instance"""
    global _browser_analyzer
    
    if not PLAYWRIGHT_AVAILABLE:
        return None
    
    if _browser_analyzer is None:
        _browser_analyzer = PlaywrightBrowserAnalyzer(headless=True)
        await _browser_analyzer.__aenter__()
    
    return _browser_analyzer


async def cleanup_browser_analyzer():
    """Cleanup browser analyzer instance"""
    global _browser_analyzer
    if _browser_analyzer:
        await _browser_analyzer.__aexit__(None, None, None)
        _browser_analyzer = None

