"""
Chutes API-powered LLM agent
Uses Chutes API for intelligent task understanding and action generation
"""
from typing import Dict, Any, List, Optional
import httpx
import json
import time
import asyncio
import hashlib
from functools import lru_cache
from .base import BaseAgent
from ..actions.converter import convert_to_iwa_action
from ..actions.selectors import create_selector
from ..utils.task_parser import TaskParser
from ..utils.action_validator import ActionValidator
from ..utils.action_sequencer import ActionSequencer
from config.settings import settings
import os


class ChutesAgent(BaseAgent):
    """LLM-powered agent using Chutes API"""
    
    def __init__(self):
        self.api_key = os.getenv("CHUTES_API_KEY", "")
        # Chutes API endpoint - use /v1/chat/completions (correct endpoint)
        self.api_url = os.getenv("CHUTES_API_URL", "https://api.chutes.ai/v1/chat/completions")
        # Model selection - default to Qwen2.5-7B (FREE and good quality!)
        self.model = os.getenv("CHUTES_MODEL", settings.chutes_model if hasattr(settings, 'chutes_model') else "Qwen/Qwen2.5-7B-Instruct")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            raise ValueError("CHUTES_API_KEY not set in environment")
        
        # Rate limiting: Track last request time to avoid hitting per-minute limits
        # Chutes API has strict per-minute limits (likely 10-20 req/min based on testing)
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Minimum 3 seconds between requests (20 req/min max)
        self._rate_limit_lock = asyncio.Lock()
        self.consecutive_429_errors = 0  # Track consecutive rate limit errors
        self.last_429_time = 0  # Track when we last got a 429
        
        # Response caching to reduce API calls
        self._response_cache: Dict[str, tuple] = {}  # {cache_key: (actions, timestamp)}
        self._cache_ttl = 300  # Cache for 5 minutes
        
        # Task parsing, validation, and sequencing
        self.task_parser = TaskParser()
        self.action_validator = ActionValidator()
        self.action_sequencer = ActionSequencer()
        
        # Try alternative API URL formats if default doesn't work
        self.alternative_urls = [
            "https://api.chutes.ai/chat/completions",  # Fallback
        ]
    
    async def _rate_limit(self):
        """Enforce rate limiting to avoid 429 errors"""
        async with self._rate_limit_lock:
            current_time = time.time()
            
            # If we've been getting 429 errors, wait longer
            if self.consecutive_429_errors > 0:
                time_since_last_429 = current_time - self.last_429_time
                # Wait at least 60 seconds after a 429 error
                if time_since_last_429 < 60:
                    wait_time = 60 - time_since_last_429
                    import logging
                    logging.info(f"Waiting {wait_time:.1f}s after rate limit error...")
                    await asyncio.sleep(wait_time)
                    # Reset counter after waiting
                    self.consecutive_429_errors = 0
            
            # Normal rate limiting between requests
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()
    
    async def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call Chutes API for LLM completion"""
        # Enforce rate limiting to avoid 429 errors
        await self._rate_limit()
        
        # Use X-API-Key header (confirmed working format)
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Use configured model, with fallback options
        # Chutes supports free models: Qwen/Qwen2.5-7B-Instruct, Qwen/Qwen3-32B
        # Also supports OpenAI models: gpt-4o-mini, gpt-4o, gpt-4, gpt-3.5-turbo
        primary_model = self.model
        
        # Smart fallback: prefer free models, then paid
        free_models = ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen3-32B", "Qwen/Qwen2.5-32B-Instruct"]
        paid_models = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
        
        # Build fallback list based on primary model
        if any(free in primary_model for free in ["Qwen", "qwen"]):
            # If using Qwen, fallback to other Qwen models, then paid
            fallback_models = [m for m in free_models if m != primary_model] + paid_models
        else:
            # If using paid, fallback to free first (save money!), then other paid
            fallback_models = free_models + [m for m in paid_models if m != primary_model]
        
        models_to_try = [primary_model] + fallback_models
        
        payloads = [
            {
                "model": model,
                "messages": messages,
                "temperature": 0.2,  # Lower temperature for more deterministic, consistent actions
                "max_tokens": 1500,  # Increased for more complex tasks
                "top_p": 0.9,  # Nucleus sampling for better quality
            }
            for model in models_to_try
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
                        # Rate limited - track this and wait much longer
                        self.consecutive_429_errors += 1
                        self.last_429_time = time.time()
                        
                        # If we've hit multiple 429s, wait even longer (exponential backoff)
                        wait_time = min(60 * (2 ** min(self.consecutive_429_errors - 1, 3)), 300)  # Max 5 minutes
                        
                        import logging
                        logging.warning(f"Chutes API rate limited (429). Waiting {wait_time}s before retry (attempt {self.consecutive_429_errors})...")
                        await asyncio.sleep(wait_time)
                        
                        # Retry once after waiting
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
                                # Reset error counter on success
                                self.consecutive_429_errors = 0
                                # Update rate limit to be more conservative
                                self.min_request_interval = max(self.min_request_interval, 5.0)
                                return content
                        
                        # If still rate limited after waiting, raise to trigger fallback
                        raise Exception(f"Rate limited - Chutes API per-minute limit exceeded after {wait_time}s wait. Falling back to template agent.")
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
    
    def _get_cache_key(self, prompt: str, url: str) -> str:
        """Generate cache key for prompt+url"""
        key_string = f"{prompt}|{url}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached response if available and not expired"""
        if cache_key in self._response_cache:
            actions, timestamp = self._response_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                import logging
                logging.info(f"Using cached response for task")
                return actions
            else:
                # Expired, remove from cache
                del self._response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, actions: List[Dict[str, Any]]):
        """Cache response for future use"""
        self._response_cache[cache_key] = (actions, time.time())
        # Limit cache size (keep last 100 entries)
        if len(self._response_cache) > 100:
            # Remove oldest entry
            oldest_key = min(self._response_cache.keys(), 
                           key=lambda k: self._response_cache[k][1])
            del self._response_cache[oldest_key]
    
    async def _generate_actions_with_llm(self, prompt: str, url: str, parsed_task: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Use LLM to generate action sequence with caching"""
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, url)
        cached_actions = self._get_cached_response(cache_key)
        if cached_actions:
            return cached_actions
        
        # Parse task if not provided
        if parsed_task is None:
            parsed_task = self.task_parser.parse_task(prompt, url)
        
        system_prompt = """You are an expert web automation agent. Generate precise, efficient browser action sequences to complete tasks.

CRITICAL RULES:
1. Always start with NavigateAction if URL is provided
2. Add WaitAction (1-2 seconds) after navigation for page load
3. Take ScreenshotAction after important state changes
4. Use specific selectors - prefer tagContainsSelector for buttons/links, attributeValueSelector for inputs
5. Add WaitAction (0.3-0.5s) between interactions for stability
6. Be concise - only necessary actions, avoid redundant screenshots

ACTION TYPES:
- NavigateAction: Navigate to URL (requires "url" field)
- ClickAction: Click element (requires "selector" field)
- TypeAction: Type text (requires "selector" and "text" fields)
- WaitAction: Wait duration (requires "time_seconds" field, typically 0.3-2.0)
- ScreenshotAction: Capture page state (no fields needed)
- ScrollAction: Scroll page (optional "direction" and "pixels")

SELECTOR TYPES (in priority order):
1. tagContainsSelector: Match visible text (e.g., "Login", "Submit", "Save")
   - Best for: Buttons, links, labels
   - Format: {"type": "tagContainsSelector", "value": "Login", "case_sensitive": false}
   
2. attributeValueSelector: Match HTML attributes
   - Best for: Input fields, form elements
   - Format: {"type": "attributeValueSelector", "value": "username", "attribute": "name", "case_sensitive": false}
   - Common attributes: name, id, type, data-testid, aria-label
   
3. xpathSelector: XPath expression (use only if necessary)
   - Format: {"type": "xpathSelector", "value": "//button[@type='submit']"}

SELECTOR STRATEGY:
- For buttons/links: Use tagContainsSelector with button text
- For inputs: Use attributeValueSelector with name/id/type
- For forms: Try name attribute first, then type, then id
- Always set case_sensitive: false unless exact case matters

TASK PATTERNS:
- Login: Navigate → Wait → Screenshot → Type username → Type password → Click login → Wait → Screenshot
- Form fill: Navigate → Wait → Screenshot → Type each field → Click submit → Wait → Screenshot
- Click task: Navigate → Wait → Screenshot → Click target → Wait → Screenshot
- Search: Navigate → Wait → Screenshot → Type in search box → Click search/submit → Wait → Screenshot

EXTRACTION RULES:
- Extract credentials from prompt: "username:user123" → username="user123"
- Extract URLs: "navigate to https://example.com" → NavigateAction with that URL
- Extract text to type: "type 'hello'" → TypeAction with text="hello"
- Extract target elements: "click the login button" → ClickAction with selector for "Login"

Return ONLY valid JSON array. No explanations, no markdown, just JSON."""
        
        # Build enhanced prompt with extracted information
        prompt_parts = [f"Task: {prompt}"]
        prompt_parts.append(f"URL: {parsed_task.get('url') or url}")
        
        # Add extracted information
        if parsed_task.get("credentials"):
            creds = parsed_task["credentials"]
            if "username" in creds:
                prompt_parts.append(f"Username: {creds['username']}")
            if "password" in creds:
                prompt_parts.append(f"Password: {creds['password']}")
            if "email" in creds:
                prompt_parts.append(f"Email: {creds['email']}")
        
        if parsed_task.get("text_to_type"):
            prompt_parts.append(f"Text to type: '{parsed_task['text_to_type']}'")
        
        if parsed_task.get("target_element"):
            prompt_parts.append(f"Target element: {parsed_task['target_element']}")
        
        # Add task type hints
        if parsed_task.get("has_login"):
            prompt_parts.append("Task type: Login required")
        if parsed_task.get("has_form"):
            prompt_parts.append("Task type: Form filling")
        if parsed_task.get("has_search"):
            prompt_parts.append("Task type: Search")
        if parsed_task.get("has_modify"):
            prompt_parts.append("Task type: Modification/Edit")
        
        user_prompt = "\n".join(prompt_parts) + f"""

Analyze the task and generate a precise action sequence using the extracted information above.

Return ONLY a valid JSON array of actions. Example format:
[
  {{"type": "NavigateAction", "url": "{parsed_task.get('url') or url}"}},
  {{"type": "WaitAction", "time_seconds": 1.5}},
  {{"type": "ScreenshotAction"}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Login", "case_sensitive": false}}}}
]

JSON only, no other text:"""
        
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
            
            # Cache the response
            self._cache_response(cache_key, actions)
            
            return actions
            
        except json.JSONDecodeError as e:
            # Fallback to template if LLM returns invalid JSON
            import logging
            logging.warning(f"Chutes LLM returned invalid JSON, falling back to template: {e}")
            from .template import TemplateAgent
            template_agent = TemplateAgent()
            return await template_agent.solve_task("", prompt, url)
        except Exception as e:
            # Fallback to template on error
            import logging
            error_msg = str(e)
            if "Rate limited" in error_msg or "429" in error_msg:
                logging.warning(f"Chutes API rate limited, falling back to template agent")
            else:
                logging.warning(f"Chutes API error, falling back to template: {error_msg}")
            from .template import TemplateAgent
            template_agent = TemplateAgent()
            return await template_agent.solve_task("", prompt, url)
    
    async def solve_task(
        self, 
        task_id: str, 
        prompt: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """Solve task using Chutes LLM with validation and error handling"""
        import logging
        try:
            # Parse task to extract information
            parsed_task = self.task_parser.parse_task(prompt, url)
            logging.info(f"Using Chutes LLM (model: {self.model}) for task: {prompt[:50]}...")
            
            # Use parsed URL if extracted
            task_url = parsed_task.get("url") or url
            
            # Generate actions using LLM (pass parsed_task to avoid re-parsing)
            raw_actions = await self._generate_actions_with_llm(prompt, task_url, parsed_task)
            
            logging.info(f"Chutes LLM generated {len(raw_actions)} actions")
            
            # Convert to IWA format and fix common issues
            iwa_actions = []
            for action in raw_actions:
                # Fix common issues first
                action = self.action_validator.fix_common_issues(action)
                # Convert to IWA format
                iwa_action = convert_to_iwa_action(action)
                iwa_actions.append(iwa_action)
            
            # Validate actions
            valid_actions, errors = self.action_validator.validate_actions(iwa_actions)
            
            if errors:
                logging.warning(f"Action validation found {len(errors)} errors: {errors[:3]}")
            
            # Use valid actions, or fallback if none valid
            if valid_actions:
                iwa_actions = valid_actions
            elif iwa_actions:
                # If we have actions but validation failed, log and use them anyway
                logging.warning(f"Using actions despite validation errors")
            else:
                # No valid actions, ensure non-empty
                iwa_actions = [{"type": "ScreenshotAction"}]
            
            # Optimize action sequence
            iwa_actions = self.action_sequencer.optimize_sequence(iwa_actions)
            iwa_actions = self.action_sequencer.add_smart_waits(iwa_actions)
            
            logging.info(f"Returning {len(iwa_actions)} optimized actions")
            return iwa_actions
            
        except Exception as e:
            # Fallback to template agent on error
            import logging
            error_msg = str(e)
            if "Rate limited" in error_msg or "429" in error_msg:
                logging.warning(f"Chutes API rate limited, using template fallback")
            else:
                logging.warning(f"Chutes API error, using template fallback: {error_msg}")
            from .template import TemplateAgent
            template_agent = TemplateAgent()
            return await template_agent.solve_task(task_id, prompt, url)

