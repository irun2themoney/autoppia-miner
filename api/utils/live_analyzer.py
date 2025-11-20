"""
Live Analysis Module
Fetches real page content and generates verified selectors based on DOM analysis.
"""
import httpx
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional, Tuple
import re
import asyncio

logger = logging.getLogger(__name__)

class LiveAnalyzer:
    """
    Analyzes live web pages to generate robust selectors.
    """
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from the URL.
        Returns None if fetch fails.
        """
        if not url or not url.startswith("http"):
            return None
            
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return None

    def analyze_dom(self, html: str, intent: str, task_type: str = "generic") -> List[Dict[str, Any]]:
        """
        Parse HTML and find elements matching the intent.
        Returns a list of potential selectors sorted by confidence.
        """
        if not html:
            return []
            
        try:
            soup = BeautifulSoup(html, "lxml")
            # Remove scripts and styles to reduce noise
            for script in soup(["script", "style", "meta", "noscript"]):
                script.decompose()
                
            candidates = []
            
            # Strategy based on task type
            if task_type == "login":
                candidates.extend(self._find_login_elements(soup, intent))
            elif task_type == "job_apply":
                candidates.extend(self._find_job_elements(soup, intent))
            else:
                # Generic search for clickable elements matching intent keywords
                candidates.extend(self._find_generic_elements(soup, intent))
                
            return candidates
            
        except Exception as e:
            logger.error(f"Error analyzing DOM: {e}")
            return []

    def _find_login_elements(self, soup: BeautifulSoup, intent: str) -> List[Dict[str, Any]]:
        """Find login-related fields and buttons"""
        selectors = []
        
        # Common login field names
        user_terms = ["user", "login", "email", "username"]
        pass_terms = ["pass", "pwd", "secret"]
        submit_terms = ["sign in", "log in", "submit", "enter"]
        
        # Find inputs
        for input_tag in soup.find_all("input"):
            attrs = input_tag.attrs
            score = 0
            field_type = "unknown"
            
            # Check attributes for matches
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
                    
        # Find buttons
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
        
        # Find "Apply" buttons
        for tag in soup.find_all(["button", "a", "div", "span"]):
            text = tag.get_text().strip().lower()
            
            # Exact match is high confidence
            if text in apply_terms:
                selector = self._generate_selector(tag)
                if selector:
                    selectors.append({
                        "selector": selector,
                        "type": "apply_button",
                        "confidence": 0.95,
                        "text": text
                    })
            # Partial match
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
            
            # Boost for clickable tags
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
            # 1. ID selector (Best)
            if tag.has_attr("id"):
                # Check if ID looks dynamic (too long, random chars)
                id_val = tag["id"]
                if len(id_val) < 30 and not re.search(r'\d{5,}', id_val):
                    return f"#{id_val}"
            
            # 2. Unique Class selector
            if tag.has_attr("class"):
                classes = tag["class"]
                # Filter out common utility classes
                valid_classes = [c for c in classes if c not in ["btn", "button", "active", "hidden", "visible"]]
                if valid_classes:
                    return f".{'.'.join(valid_classes)}"
            
            # 3. Attribute selector (Name, Type, Data-*)
            for attr in ["name", "type", "data-testid", "data-id", "aria-label", "placeholder"]:
                if tag.has_attr(attr):
                    return f'{tag.name}[{attr}="{tag[attr]}"]'
            
            # 4. Text content selector (Pseudo-selector for Playwright/Puppeteer)
            # Note: Standard CSS doesn't support :text, but many automation tools do.
            # We'll stick to standard CSS or XPath if needed, but for now let's try a specific attribute path
            
            # 5. Fallback: Tag + Hierarchy (simplified)
            # This is weak, but better than nothing
            path = []
            parent = tag
            while parent and parent.name != "[document]":
                path.insert(0, parent.name)
                parent = parent.parent
                if len(path) > 3: break # Limit depth
                
            return " > ".join(path)
            
        except Exception:
            return None

# Global instance
live_analyzer = LiveAnalyzer()
