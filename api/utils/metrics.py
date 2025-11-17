"""Performance metrics and monitoring"""
from typing import Dict, Any
import time
from collections import defaultdict, deque
from datetime import datetime


class MetricsCollector:
    """Collect and track performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "llm_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "template_fallbacks": 0,
            "rate_limit_errors": 0,
            "validation_errors": 0,
            "avg_response_time": 0.0,
            "response_times": deque(maxlen=100),  # Keep last 100 response times
        }
        
        self.task_metrics = defaultdict(int)  # Track task types
        self.error_counts = defaultdict(int)  # Track error types
    
    def record_request(self, success: bool, response_time: float, task_type: str = "unknown"):
        """Record a request"""
        self.metrics["total_requests"] += 1
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
        
        self.metrics["response_times"].append(response_time)
        self.metrics["avg_response_time"] = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        self.task_metrics[task_type] += 1
    
    def record_llm_call(self):
        """Record LLM API call"""
        self.metrics["llm_calls"] += 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics["cache_misses"] += 1
    
    def record_template_fallback(self):
        """Record template fallback"""
        self.metrics["template_fallbacks"] += 1
    
    def record_rate_limit_error(self):
        """Record rate limit error"""
        self.metrics["rate_limit_errors"] += 1
    
    def record_validation_error(self, error_type: str):
        """Record validation error"""
        self.metrics["validation_errors"] += 1
        self.error_counts[error_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        cache_total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (self.metrics["cache_hits"] / cache_total * 100) if cache_total > 0 else 0
        
        success_rate = (self.metrics["successful_requests"] / self.metrics["total_requests"] * 100) if self.metrics["total_requests"] > 0 else 0
        
        return {
            **self.metrics,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "success_rate": round(success_rate, 2),
            "task_types": dict(self.task_metrics),
            "error_types": dict(self.error_counts),
            "timestamp": datetime.now().isoformat(),
        }
    
    def reset(self):
        """Reset metrics"""
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "llm_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "template_fallbacks": 0,
            "rate_limit_errors": 0,
            "validation_errors": 0,
            "avg_response_time": 0.0,
            "response_times": deque(maxlen=100),
        }
        self.task_metrics.clear()
        self.error_counts.clear()


# Global metrics instance
metrics = MetricsCollector()

