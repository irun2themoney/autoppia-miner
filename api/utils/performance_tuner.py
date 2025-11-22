"""Auto-tuning performance optimizer - dynamically adjusts settings for maximum performance"""
from typing import Dict, Any
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)


class PerformanceTuner:
    """
    Auto-tuning system that dynamically adjusts performance settings
    based on real-time metrics to maximize TAO earnings
    """
    
    def __init__(self):
        self.response_time_history = deque(maxlen=100)
        self.success_rate_history = deque(maxlen=100)
        self.cache_hit_rate_history = deque(maxlen=100)
        
        # Tunable parameters
        self.cache_aggressiveness = 0.95  # Similarity threshold (0.0-1.0)
        self.cache_ttl = 1200  # Cache TTL in seconds
        self.max_cache_size = 500
        
        # Performance targets
        self.target_response_time = 1.5  # Target: <1.5s average
        self.target_success_rate = 0.85  # Target: >85% success
        self.target_cache_hit_rate = 0.50  # Target: >50% cache hits
        
        self.last_tune_time = time.time()
        self.tune_interval = 300  # Tune every 5 minutes
    
    def record_metrics(
        self,
        response_time: float,
        success: bool,
        cache_hit: bool
    ):
        """Record metrics for auto-tuning"""
        self.response_time_history.append(response_time)
        self.success_rate_history.append(1.0 if success else 0.0)
        self.cache_hit_rate_history.append(1.0 if cache_hit else 0.0)
        
        # Auto-tune periodically
        if time.time() - self.last_tune_time > self.tune_interval:
            self._auto_tune()
            self.last_tune_time = time.time()
    
    def _auto_tune(self):
        """Automatically tune performance parameters based on metrics"""
        if len(self.response_time_history) < 10:
            return  # Not enough data
        
        avg_response_time = sum(self.response_time_history) / len(self.response_time_history)
        avg_success_rate = sum(self.success_rate_history) / len(self.success_rate_history)
        avg_cache_hit_rate = sum(self.cache_hit_rate_history) / len(self.cache_hit_rate_history)
        
        logger.info(f"Performance Tuner: Response={avg_response_time:.2f}s, "
                   f"Success={avg_success_rate:.2%}, Cache={avg_cache_hit_rate:.2%}")
        
        # Tune cache aggressiveness based on success rate and response time
        if avg_response_time > self.target_response_time and avg_cache_hit_rate < self.target_cache_hit_rate:
            # Too slow and low cache hits - increase cache aggressiveness
            self.cache_aggressiveness = min(0.98, self.cache_aggressiveness + 0.01)
            logger.info(f"Performance Tuner: Increased cache aggressiveness to {self.cache_aggressiveness:.2f}")
        elif avg_success_rate < self.target_success_rate and avg_cache_hit_rate > 0.6:
            # Low success rate but high cache hits - might be overfitting, reduce aggressiveness
            self.cache_aggressiveness = max(0.90, self.cache_aggressiveness - 0.01)
            logger.info(f"Performance Tuner: Decreased cache aggressiveness to {self.cache_aggressiveness:.2f}")
        
        # Tune cache TTL based on response time
        if avg_response_time > self.target_response_time:
            # Increase TTL to keep more items cached longer
            self.cache_ttl = min(1800, self.cache_ttl + 60)
            logger.info(f"Performance Tuner: Increased cache TTL to {self.cache_ttl}s")
        elif avg_response_time < self.target_response_time * 0.8:
            # Very fast - can reduce TTL to free memory
            self.cache_ttl = max(600, self.cache_ttl - 60)
            logger.info(f"Performance Tuner: Decreased cache TTL to {self.cache_ttl}s")
    
    def get_optimal_cache_settings(self) -> Dict[str, Any]:
        """Get optimal cache settings based on auto-tuning"""
        return {
            "similarity_threshold": self.cache_aggressiveness,
            "ttl": self.cache_ttl,
            "max_size": self.max_cache_size
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for monitoring"""
        if len(self.response_time_history) == 0:
            return {
                "avg_response_time": 0.0,
                "avg_success_rate": 0.0,
                "avg_cache_hit_rate": 0.0,
                "cache_aggressiveness": self.cache_aggressiveness,
                "cache_ttl": self.cache_ttl
            }
        
        return {
            "avg_response_time": sum(self.response_time_history) / len(self.response_time_history),
            "avg_success_rate": sum(self.success_rate_history) / len(self.success_rate_history),
            "avg_cache_hit_rate": sum(self.cache_hit_rate_history) / len(self.cache_hit_rate_history),
            "cache_aggressiveness": self.cache_aggressiveness,
            "cache_ttl": self.cache_ttl,
            "targets": {
                "response_time": self.target_response_time,
                "success_rate": self.target_success_rate,
                "cache_hit_rate": self.target_cache_hit_rate
            }
        }


# Global instance
performance_tuner = PerformanceTuner()

