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
import re
from functools import lru_cache
from .base import BaseAgent
from ..actions.converter import convert_to_iwa_action
from ..actions.selectors import create_selector
from ..utils.task_parser import TaskParser
from ..utils.action_validator import ActionValidator
from ..utils.action_sequencer import ActionSequencer
from ..utils.action_optimizer import ActionOptimizer
from ..utils.error_recovery import ErrorRecovery
from ..utils.selector_enhancer import SelectorEnhancer
from ..utils.visual_selectors import VisualSelectorGenerator
from ..utils.feedback_loop import FeedbackLoop
from ..utils.ensemble_generator import EnsembleGenerator
from ..utils.performance_optimizer import PerformanceOptimizer
from ..utils.adaptive_retry import AdaptiveRetry
from ..utils.metrics import metrics
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
        # Chutes Support Recommendation: "Space out your requests — avoid sending large bursts"
        # IMPORTANT: Chutes has separate per-minute/per-hour limits from daily quota
        # Start conservative: 5 seconds between requests (12 req/min) to avoid bursts
        self.last_request_time = 0
        self.min_request_interval = 5.0  # 5 seconds between requests (12 req/min) - conservative to avoid bursts
        self._rate_limit_lock = asyncio.Lock()
        self.consecutive_429_errors = 0  # Track consecutive rate limit errors (resets on restart)
        self.last_429_time = 0  # Track when we last got a 429 (resets on restart)
        self.rate_limit_info = {}  # Store rate limit info from headers
        
        # Response caching to reduce API calls (using smart cache)
        from ..utils.smart_cache import SmartCache
        self._response_cache = SmartCache(max_size=100, ttl=300)  # 5 minute TTL
        
        # Task parsing, validation, sequencing, optimization, error recovery, selector enhancement, and feedback
        self.task_parser = TaskParser()
        self.action_validator = ActionValidator()
        self.action_sequencer = ActionSequencer()
        self.action_optimizer = ActionOptimizer()
        self.error_recovery = ErrorRecovery(max_retries=2)
        self.selector_enhancer = SelectorEnhancer()
        self.visual_selector_gen = VisualSelectorGenerator()
        self.feedback_loop = FeedbackLoop()
        self.ensemble_gen = EnsembleGenerator()
        self.performance_optimizer = PerformanceOptimizer()
        self.adaptive_retry = AdaptiveRetry(max_retries=3)
        
        # Try alternative API URL formats if default doesn't work
        self.alternative_urls = [
            "https://api.chutes.ai/chat/completions",  # Fallback
        ]
    
    async def _rate_limit(self):
        """Enforce rate limiting to avoid 429 errors - PERSISTENT: Will wait until it works"""
        async with self._rate_limit_lock:
            current_time = time.time()
            
            # Chutes Support Recommendation: "Implement exponential backoff — in case of 429 responses"
            # If we've been getting 429 errors, implement exponential backoff
            if self.consecutive_429_errors > 0:
                time_since_last_429 = current_time - self.last_429_time
                # If it's been more than 5 minutes since last 429, reset (rate limit window likely passed)
                if time_since_last_429 > 300:  # 5 minutes
                    # Rate limit window likely reset, clear the error counter
                    self.consecutive_429_errors = 0
                    import logging
                    logging.info("Rate limit window likely reset, clearing error counter")
                elif time_since_last_429 < 60:
                    # Exponential backoff: wait 60s, 120s, 240s, 480s (1min, 2min, 4min, 8min)
                    backoff_times = [60, 120, 240, 480]  # Exponential backoff
                    backoff_index = min(self.consecutive_429_errors - 1, len(backoff_times) - 1)
                    wait_time = backoff_times[backoff_index] - time_since_last_429
                    if wait_time > 0:
                        import logging
                        logging.info(f"Exponential backoff: Waiting {wait_time:.1f}s after rate limit error (attempt {self.consecutive_429_errors})...")
                        await asyncio.sleep(wait_time)
                    # Reset counter after waiting
                    self.consecutive_429_errors = 0
            
            # Normal rate limiting between requests - but be smarter about it
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
                        # Extract rate limit info from headers (if available)
                        rate_limit_limit = response.headers.get("X-RateLimit-Limit")
                        rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
                        rate_limit_reset = response.headers.get("X-RateLimit-Reset")
                        
                        if rate_limit_limit:
                            self.rate_limit_info = {
                                "limit": rate_limit_limit,
                                "remaining": rate_limit_remaining,
                                "reset": rate_limit_reset
                            }
                            import logging
                            logging.debug(f"Rate limit info: {self.rate_limit_info}")
                        
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
                        # Rate limited - PERSISTENT RETRY: Keep trying until it works!
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                wait_time = int(retry_after)
                                import logging
                                logging.warning(f"Chutes API rate limited (429). Retry-After header says wait {wait_time}s...")
                            except:
                                wait_time = 30  # Default if header is invalid
                        else:
                            # No Retry-After header, use exponential backoff (Chutes Support Recommendation)
                            self.consecutive_429_errors += 1
                            self.last_429_time = time.time()
                            
                            # Exponential backoff: 60s, 120s, 240s, 480s (1min, 2min, 4min, 8min)
                            # Chutes Support: "Implement exponential backoff — in case of 429 responses"
                            backoff_times = [60, 120, 240, 480, 600]  # Extended: up to 10 minutes
                            backoff_index = min(self.consecutive_429_errors - 1, len(backoff_times) - 1)
                            wait_time = backoff_times[backoff_index]
                            
                            import logging
                            logging.warning(f"Chutes API rate limited (429). Exponential backoff: Waiting {wait_time}s before retry (attempt {self.consecutive_429_errors})...")
                        
                        # PERSISTENT: Wait and retry with increasing patience
                        await asyncio.sleep(wait_time)
                        
                        # PERSISTENT RETRY: Try multiple times with increasing delays
                        max_retries = 5  # Try up to 5 times
                        for retry_attempt in range(max_retries):
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
                                    # After successful retry, increase spacing slightly to avoid future bursts
                                    # Chutes Support: "Space out your requests — avoid sending large bursts"
                                    self.min_request_interval = min(self.min_request_interval + 1.0, 10.0)  # Cap at 10s
                                    import logging
                                    logging.info(f"✅ Chutes API SUCCESS after {retry_attempt + 1} retries! Increased request spacing to {self.min_request_interval}s")
                                    return content
                            
                            elif retry_response.status_code == 429:
                                # Still rate limited - wait longer and try again
                                next_wait = wait_time * (retry_attempt + 2)  # Progressive wait: 2x, 3x, 4x, 5x
                                import logging
                                logging.warning(f"Still rate limited after {retry_attempt + 1} retries. Waiting {next_wait}s before next attempt...")
                                await asyncio.sleep(next_wait)
                                continue
                            else:
                                # Different error - break and try next URL/model
                                break
                        
                        # If we exhausted retries, try next URL/model instead of giving up
                        import logging
                        logging.warning(f"Rate limited after {max_retries} retries. Trying next URL/model...")
                        continue  # Try next URL/model combination
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
        
                # PERSISTENT: If all endpoints/models failed, wait and retry the whole process
                import logging
                logging.warning(f"All Chutes API endpoints/models failed. Waiting 60s and retrying entire request...")
                await asyncio.sleep(60)  # Wait 1 minute
                # Retry the entire function call (will be caught by outer retry logic)
                raise Exception(f"Failed to call Chutes API after trying all endpoints. Will retry: {last_error}")
    
    def _get_cached_response(self, prompt: str, url: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached response if available"""
        cached = self._response_cache.get(prompt, url)
        if cached:
            import logging
            logging.info(f"Using cached response for task")
        return cached
    
    def _cache_response(self, prompt: str, url: str, actions: List[Dict[str, Any]]):
        """Cache response for future use"""
        self._response_cache.set(prompt, url, actions)
    
    async def _generate_actions_with_llm(self, prompt: str, url: str, parsed_task: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Use LLM to generate action sequence with caching"""
        
        # Check cache first
        cached_actions = self._get_cached_response(prompt, url)
        if cached_actions:
            metrics.record_cache_hit()
            return cached_actions
        
        metrics.record_cache_miss()
        
        # Parse task if not provided
        if parsed_task is None:
            parsed_task = self.task_parser.parse_task(prompt, url)
        
        system_prompt = """You are an expert web automation agent. Use chain-of-thought reasoning to generate precise, efficient browser action sequences.

THINKING PROCESS:
1. Analyze the task requirements carefully
2. Identify the key actions needed (navigate, interact, submit)
3. Determine the best selectors for each element
4. Plan the sequence logically
5. Add appropriate waits for stability
6. Include screenshots for verification

Generate actions that are:
- Logical and sequential
- Efficient (no redundant steps)
- Robust (multiple selector strategies)
- Complete (all required actions)

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

Return ONLY valid JSON array. No explanations, no markdown, just JSON.

EXAMPLES:

Example 1 - Login task:
Input: "Login with username:user123 and password:pass456"
Output:
[
  {{"type": "NavigateAction", "url": "{parsed_task.get('url') or url}"}},
  {{"type": "WaitAction", "time_seconds": 1.5}},
  {{"type": "ScreenshotAction"}},
  {{"type": "TypeAction", "selector": {{"type": "attributeValueSelector", "value": "username", "attribute": "name", "case_sensitive": false}}, "text": "user123"}},
  {{"type": "TypeAction", "selector": {{"type": "attributeValueSelector", "value": "password", "attribute": "type", "case_sensitive": false}}, "text": "pass456"}},
  {{"type": "WaitAction", "time_seconds": 0.3}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Login", "case_sensitive": false}}}},
  {{"type": "WaitAction", "time_seconds": 2.0}},
  {{"type": "ScreenshotAction"}}
]

Example 2 - Click task:
Input: "Click the month view button"
Output:
[
  {{"type": "NavigateAction", "url": "{parsed_task.get('url') or url}"}},
  {{"type": "WaitAction", "time_seconds": 1.5}},
  {{"type": "ScreenshotAction"}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Month", "case_sensitive": false}}}},
  {{"type": "WaitAction", "time_seconds": 1.0}},
  {{"type": "ScreenshotAction"}}
]

Example 3 - Form fill:
Input: "Fill the form with name: John and email: john@example.com"
Output:
[
  {{"type": "NavigateAction", "url": "{parsed_task.get('url') or url}"}},
  {{"type": "WaitAction", "time_seconds": 1.5}},
  {{"type": "ScreenshotAction"}},
  {{"type": "TypeAction", "selector": {{"type": "attributeValueSelector", "value": "name", "attribute": "name", "case_sensitive": false}}, "text": "John"}},
  {{"type": "WaitAction", "time_seconds": 0.3}},
  {{"type": "TypeAction", "selector": {{"type": "attributeValueSelector", "value": "email", "attribute": "name", "case_sensitive": false}}, "text": "john@example.com"}},
  {{"type": "WaitAction", "time_seconds": 0.3}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Submit", "case_sensitive": false}}}},
  {{"type": "WaitAction", "time_seconds": 1.0}},
  {{"type": "ScreenshotAction"}}
]

Example 4 - Search task:
Input: "Search for 'python tutorial'"
Output:
[
  {{"type": "NavigateAction", "url": "{parsed_task.get('url') or url}"}},
  {{"type": "WaitAction", "time_seconds": 1.5}},
  {{"type": "ScreenshotAction"}},
  {{"type": "TypeAction", "selector": {{"type": "attributeValueSelector", "value": "search", "attribute": "name", "case_sensitive": false}}, "text": "python tutorial"}},
  {{"type": "WaitAction", "time_seconds": 0.5}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Search", "case_sensitive": false}}}},
  {{"type": "WaitAction", "time_seconds": 2.0}},
  {{"type": "ScreenshotAction"}}
]

Example 5 - Multi-step task:
Input: "Click on the calendar, then select the month view"
Output:
[
  {{"type": "NavigateAction", "url": "{parsed_task.get('url') or url}"}},
  {{"type": "WaitAction", "time_seconds": 1.5}},
  {{"type": "ScreenshotAction"}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Calendar", "case_sensitive": false}}}},
  {{"type": "WaitAction", "time_seconds": 1.0}},
  {{"type": "ScreenshotAction"}},
  {{"type": "ClickAction", "selector": {{"type": "tagContainsSelector", "value": "Month", "case_sensitive": false}}}},
  {{"type": "WaitAction", "time_seconds": 1.0}},
  {{"type": "ScreenshotAction"}}
]

CRITICAL RULES:
1. ALWAYS start with NavigateAction if URL is provided
2. ALWAYS take ScreenshotAction after navigation (wait 1.5s first)
3. ALWAYS take ScreenshotAction after important actions (clicks, form submissions)
4. Use WaitAction between actions (0.3-0.5s for typing, 1.0-2.0s for clicks)
5. Use multiple selector strategies for ClickAction (fallback chain)
6. Extract credentials/text from prompt and use in TypeAction
7. Keep actions logical and sequential
8. Return ONLY valid JSON array, no explanations"""
        
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
            
            # Remove markdown code blocks
            if llm_response.startswith("```json"):
                llm_response = llm_response[7:]
            elif llm_response.startswith("```"):
                llm_response = llm_response[3:]
            if llm_response.endswith("```"):
                llm_response = llm_response[:-3]
            llm_response = llm_response.strip()
            
            # Try to extract JSON if wrapped in text
            json_start = llm_response.find("[")
            json_end = llm_response.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                llm_response = llm_response[json_start:json_end]
            
            # Parse JSON with better error handling
            try:
                actions = json.loads(llm_response)
            except json.JSONDecodeError as e:
                # Try to fix common JSON issues
                # Remove trailing commas
                llm_response = re.sub(r',\s*}', '}', llm_response)
                llm_response = re.sub(r',\s*]', ']', llm_response)
                try:
                    actions = json.loads(llm_response)
                except:
                    raise json.JSONDecodeError(f"Failed to parse LLM response as JSON: {e}")
            
            if not isinstance(actions, list):
                actions = [actions]
            
            # Cache the response
            self._cache_response(prompt, url, actions)
            
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
        """Solve task using Chutes LLM with validation and error handling - PERSISTENT: Will keep trying until it works"""
        import logging
        start_time = time.time()
        
        # PERSISTENT RETRY: Try up to 3 times with increasing patience
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Parse task to extract information
                parsed_task = self.task_parser.parse_task(prompt, url)
                logging.info(f"Using Chutes LLM (model: {self.model}) for task: {prompt[:50]}...")
                
                # Use parsed URL if extracted
                task_url = parsed_task.get("url") or url
                
                # Generate actions using LLM (pass parsed_task to avoid re-parsing)
                metrics.record_llm_call()
                raw_actions = await self._generate_actions_with_llm(prompt, task_url, parsed_task)
                
                logging.info(f"Chutes LLM generated {len(raw_actions)} actions")
                
                # Convert to IWA format and enhance selectors
                iwa_actions = []
                for action in raw_actions:
                action_type = action.get("type", "")
                
                # Enhance selectors for ClickAction with visual and feedback-based strategies
                if action_type == "ClickAction" and action.get("selector"):
                    original_selector = action["selector"]
                    
                    # Get base enhanced selectors
                    enhanced = self.selector_enhancer.enhance_selector(
                        original_selector,
                        prompt,
                        "click"
                    )
                    
                    # Add visual/contextual selectors
                    if original_selector.get("value"):
                        visual_selectors = self.visual_selector_gen.generate_priority_selectors(
                            original_selector.get("value"),
                            "button"
                        )
                        # Merge visual selectors at the beginning (higher priority)
                        enhanced = visual_selectors[:3] + enhanced
                    
                    # Enhance with context
                    enhanced = self.visual_selector_gen.enhance_with_context(
                        enhanced,
                        prompt,
                        url
                    )
                    
                    # Get feedback-based best selectors
                    feedback_selectors = self.feedback_loop.get_best_selector_strategy("button", {})
                    if feedback_selectors:
                        # Prepend feedback-based selectors (highest priority)
                        enhanced = feedback_selectors[:2] + enhanced
                    
                    # Use first selector, but keep enhanced list for fallback
                    action["selector"] = enhanced[0] if enhanced else original_selector
                    # Store enhanced selectors for potential retry
                    action["_enhanced_selectors"] = enhanced[1:] if len(enhanced) > 1 else []
                
                # Enhance selectors for TypeAction (form fields)
                elif action_type == "TypeAction" and action.get("selector"):
                    selector_value = action["selector"].get("value", "").lower()
                    form_field_patterns = self.selector_enhancer.FORM_FIELD_PATTERNS
                    for field_type, patterns in form_field_patterns.items():
                        if any(pattern in selector_value for pattern in patterns):
                            field_selectors = self.selector_enhancer.get_form_field_selectors(field_type)
                            if field_selectors:
                                action["selector"] = field_selectors[0]
                                action["_enhanced_selectors"] = field_selectors[1:]
                            break
                
                # Fix common issues
                if action_type == "ClickAction" and not action.get("selector"):
                    # Add default selector if missing
                    action["selector"] = create_selector("tagContainsSelector", "button", case_sensitive=False)
                
                    iwa_action = convert_to_iwa_action(action)
                    if iwa_action:
                        iwa_actions.append(iwa_action)
                
                # Validate actions
                valid_actions, errors = self.action_validator.validate_actions(iwa_actions)
                
                if errors:
                    logging.warning(f"Action validation found {len(errors)} errors: {errors[:3]}")
                    for error in errors[:3]:
                        metrics.record_validation_error(error.split(":")[0] if ":" in error else "unknown")
                
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
                iwa_actions = self.action_optimizer.optimize(iwa_actions)
                
                # Performance optimization for speed
                iwa_actions = self.performance_optimizer.optimize_response_time(iwa_actions)
                
                logging.info(f"Returning {len(iwa_actions)} optimized actions")
                
                # Record metrics
                response_time = time.time() - start_time
                self.performance_optimizer.track_response_time(response_time)
                task_type = "login" if parsed_task.get("has_login") else "form" if parsed_task.get("has_form") else "click" if "click" in prompt.lower() else "generic"
                metrics.record_request(success=True, response_time=response_time, task_type=task_type)
                
                # Note: Feedback will be recorded when validator provides results
                # For now, we assume success if actions are generated
                # In production, this would be called after validator feedback
                
                return iwa_actions
                
            except json.JSONDecodeError as e:
                # JSON error - retry with different approach
                import logging
                if attempt < max_attempts - 1:
                    logging.warning(f"Chutes LLM returned invalid JSON (attempt {attempt + 1}/{max_attempts}). Retrying...")
                    await asyncio.sleep(2)  # Brief pause before retry
                    continue
                else:
                    logging.error(f"Chutes LLM returned invalid JSON after {max_attempts} attempts: {e}")
                    raise  # Re-raise to trigger outer fallback
                    
            except Exception as e:
                # PERSISTENT: Retry on rate limit errors
                error_msg = str(e)
                if "Rate limited" in error_msg or "429" in error_msg or "Failed to call Chutes API" in error_msg:
                    if attempt < max_attempts - 1:
                        wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                        import logging
                        logging.warning(f"Chutes API rate limited (attempt {attempt + 1}/{max_attempts}). Waiting {wait_time}s and retrying...")
                        metrics.record_rate_limit_error()
                        await asyncio.sleep(wait_time)
                        continue  # Retry!
                    else:
                        import logging
                        logging.error(f"Chutes API rate limited after {max_attempts} persistent attempts. This is unusual - key may need reset.")
                        metrics.record_rate_limit_error()
                        raise  # Re-raise to trigger outer fallback
                else:
                    # Non-rate-limit error - retry once
                    if attempt < max_attempts - 1:
                        import logging
                        logging.warning(f"Chutes API error (attempt {attempt + 1}/{max_attempts}): {error_msg}. Retrying...")
                        await asyncio.sleep(2)
                        continue
                    else:
                        import logging
                        logging.error(f"Chutes API error after {max_attempts} attempts: {error_msg}")
                        raise  # Re-raise to trigger outer fallback
        
        # If we get here, all attempts failed - this should never happen due to raises above
        import logging
        logging.error("All Chutes API attempts exhausted - this should not happen")
        raise Exception("Chutes API failed after all persistent retry attempts")

