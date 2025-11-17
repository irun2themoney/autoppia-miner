"""
Chutes API-powered LLM agent
Uses Chutes API for intelligent task understanding and action generation
"""
from typing import Dict, Any, List
import httpx
import json
from .base import BaseAgent
from ..actions.converter import convert_to_iwa_action
from ..actions.selectors import create_selector
from config.settings import settings
import os


class ChutesAgent(BaseAgent):
    """LLM-powered agent using Chutes API"""
    
    def __init__(self):
        self.api_key = os.getenv("CHUTES_API_KEY", "")
        # Chutes API endpoint - use /v1/chat/completions (correct endpoint)
        self.api_url = os.getenv("CHUTES_API_URL", "https://api.chutes.ai/v1/chat/completions")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            raise ValueError("CHUTES_API_KEY not set in environment")
        
        # Try alternative API URL formats if default doesn't work
        self.alternative_urls = [
            "https://api.chutes.ai/chat/completions",  # Fallback
        ]
    
    async def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call Chutes API for LLM completion"""
        # Use X-API-Key header (confirmed working format)
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Try different payload formats (OpenAI-compatible and alternatives)
        payloads = [
            {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 1000
            },
            {
                "model": "gpt-4",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 1000
            }
        ]
        
        # Try different URLs and payload formats
        urls_to_try = [self.api_url] + self.alternative_urls
        
        last_error = None
        for url in urls_to_try:
            for payload in payloads:
                try:
                    response = await self.client.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Try different response formats
                        content = (
                            result.get("choices", [{}])[0].get("message", {}).get("content") or
                            result.get("text") or
                            result.get("response") or
                            result.get("content")
                        )
                        if content:
                            return content
                    elif response.status_code == 401:
                        last_error = f"Authentication failed - check API key (endpoint: {url})"
                        continue  # Try next URL
                    elif response.status_code == 404:
                        continue  # Try next URL
                    elif response.status_code == 429:
                        # Rate limited - wait and retry once, then raise to trigger fallback
                        import asyncio
                        await asyncio.sleep(2)
                        # Retry once
                        retry_response = await self.client.post(
                            url,
                            headers=headers,
                            json=payload,
                            timeout=30.0
                        )
                        if retry_response.status_code == 200:
                            result = retry_response.json()
                            content = (
                                result.get("choices", [{}])[0].get("message", {}).get("content") or
                                result.get("text") or
                                result.get("response") or
                                result.get("content")
                            )
                            if content:
                                return content
                        # If still rate limited, raise to trigger fallback
                        raise Exception(f"Rate limited - Chutes API quota exceeded. Falling back to template agent.")
                    else:
                        last_error = f"API error {response.status_code}: {response.text[:200]}"
                        continue
                            
                except httpx.TimeoutException:
                    last_error = "Request timeout"
                    continue
                except Exception as e:
                    # Re-raise rate limit errors to trigger fallback
                    if "Rate limited" in str(e):
                        raise
                    last_error = str(e)
                    continue
        
        raise Exception(f"Failed to call Chutes API after trying all endpoints: {last_error}")
    
    async def _generate_actions_with_llm(self, prompt: str, url: str) -> List[Dict[str, Any]]:
        """Use LLM to generate action sequence"""
        
        system_prompt = """You are a web automation expert. Generate a sequence of browser actions to complete the given task.

Available action types:
- NavigateAction: Navigate to a URL
- ClickAction: Click an element (requires selector)
- TypeAction: Type text into an input (requires selector and text)
- WaitAction: Wait for a duration (requires time_seconds)
- ScreenshotAction: Take a screenshot
- ScrollAction: Scroll the page

Selector types:
- tagContainsSelector: Find element by text content (e.g., "Login", "Submit")
- attributeValueSelector: Find element by attribute (e.g., name="username", type="password")
- xpathSelector: XPath selector (use sparingly)

Return actions as a JSON array. Each action should have:
- type: Action type (e.g., "NavigateAction", "ClickAction")
- selector: Selector object (if needed) with type, value, and optional attribute
- text: Text to type (for TypeAction)
- url: URL to navigate to (for NavigateAction)
- time_seconds: Wait duration (for WaitAction)

Example:
[
  {"type": "NavigateAction", "url": "https://example.com"},
  {"type": "WaitAction", "time_seconds": 1.0},
  {"type": "ScreenshotAction"},
  {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Login", "case_sensitive": false}}
]

Be specific with selectors. Use multiple fallback strategies if needed."""
        
        user_prompt = f"""Task: {prompt}
URL: {url}

Generate a sequence of browser actions to complete this task. Return ONLY valid JSON array of actions, no other text."""
        
        try:
            llm_response = await self._call_llm(user_prompt, system_prompt)
            
            # Extract JSON from response (handle markdown code blocks)
            llm_response = llm_response.strip()
            if llm_response.startswith("```json"):
                llm_response = llm_response[7:]
            if llm_response.startswith("```"):
                llm_response = llm_response[3:]
            if llm_response.endswith("```"):
                llm_response = llm_response[:-3]
            llm_response = llm_response.strip()
            
            # Parse JSON
            actions = json.loads(llm_response)
            
            if not isinstance(actions, list):
                actions = [actions]
            
            return actions
            
        except json.JSONDecodeError as e:
            # Fallback to template if LLM returns invalid JSON
            from .template import TemplateAgent
            template_agent = TemplateAgent()
            return await template_agent.solve_task("", prompt, url)
        except Exception as e:
            # Fallback to template on error
            from .template import TemplateAgent
            template_agent = TemplateAgent()
            return await template_agent.solve_task("", prompt, url)
    
    async def solve_task(
        self, 
        task_id: str, 
        prompt: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """Solve task using Chutes LLM"""
        try:
            # Generate actions using LLM
            raw_actions = await self._generate_actions_with_llm(prompt, url)
            
            # Convert to IWA format
            iwa_actions = []
            for action in raw_actions:
                iwa_action = convert_to_iwa_action(action)
                iwa_actions.append(iwa_action)
            
            # Ensure non-empty
            if not iwa_actions:
                iwa_actions = [{"type": "ScreenshotAction"}]
            
            return iwa_actions
            
        except Exception as e:
            # Fallback to template agent on error
            from .template import TemplateAgent
            template_agent = TemplateAgent()
            return await template_agent.solve_task(task_id, prompt, url)

