"""Adaptive retry mechanisms with intelligent strategy selection"""
from typing import Dict, Any, List, Optional, Callable
import asyncio
import logging
import time


class AdaptiveRetry:
    """Intelligent retry with adaptive strategies"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_strategies = []
        self.strategy_success_rates = {}
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with adaptive retry"""
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                # Success - record strategy if applicable
                if attempt > 0:
                    strategy_key = self._get_strategy_key(attempt)
                    self._record_success(strategy_key)
                
                return result
                
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    # Calculate backoff with jitter
                    base_delay = 0.5 * (2 ** attempt)
                    jitter = base_delay * 0.1 * (time.time() % 1)
                    delay = base_delay + jitter
                    
                    logging.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                    
                    # Adapt strategy based on error type
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        # Longer delay for rate limits
                        await asyncio.sleep(2.0)
                else:
                    logging.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_error or Exception("All retry attempts failed")
    
    def _get_strategy_key(self, attempt: int) -> str:
        """Get strategy key for tracking"""
        return f"retry_attempt_{attempt}"
    
    def _record_success(self, strategy_key: str):
        """Record successful strategy"""
        if strategy_key not in self.strategy_success_rates:
            self.strategy_success_rates[strategy_key] = {"success": 0, "total": 0}
        
        self.strategy_success_rates[strategy_key]["success"] += 1
        self.strategy_success_rates[strategy_key]["total"] += 1
    
    def get_best_retry_strategy(self) -> Dict[str, Any]:
        """Get best retry strategy based on history"""
        if not self.strategy_success_rates:
            return {"max_retries": self.max_retries, "base_delay": 0.5}
        
        # Find strategy with highest success rate
        best_strategy = None
        best_rate = 0.0
        
        for strategy_key, stats in self.strategy_success_rates.items():
            if stats["total"] > 0:
                rate = stats["success"] / stats["total"]
                if rate > best_rate:
                    best_rate = rate
                    best_strategy = strategy_key
        
        return {
            "strategy": best_strategy,
            "success_rate": best_rate,
            "max_retries": self.max_retries,
        }

