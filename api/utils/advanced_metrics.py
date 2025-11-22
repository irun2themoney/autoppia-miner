"""Advanced metrics collection for real-time monitoring"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import logging

logger = logging.getLogger(__name__)


class AdvancedMetrics:
    """
    Advanced metrics collection for top-tier monitoring
    Tracks everything needed to become #1 miner
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        
        # Real-time metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Response time tracking
        self.response_times = deque(maxlen=max_history)
        self.avg_response_time = 0.0
        self.p95_response_time = 0.0
        self.p99_response_time = 0.0
        
        # Success rate by task type
        self.task_type_stats = defaultdict(lambda: {"success": 0, "total": 0})
        
        # Error tracking
        self.error_types = defaultdict(int)
        self.recent_errors = deque(maxlen=100)
        
        # Validator activity
        self.validator_ips = defaultdict(int)
        self.validator_activity = deque(maxlen=100)
        
        # Performance trends (last hour)
        self.hourly_success_rate = deque(maxlen=60)  # 1 data point per minute
        self.hourly_response_time = deque(maxlen=60)
        
        # Cache performance
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Agent performance
        self.agent_performance = {
            "template": {"success": 0, "total": 0, "avg_time": 0.0},
            "hybrid": {"success": 0, "total": 0, "avg_time": 0.0},
        }
        
        # Vector memory stats
        self.vector_memory_recalls = 0
        self.vector_memory_hits = 0
        
        # Mutation detection stats
        self.mutations_detected = 0
        self.mutations_handled = 0
        
        self.start_time = time.time()
    
    def record_request(
        self,
        success: bool,
        response_time: float,
        task_type: str = "unknown",
        agent_type: str = "hybrid",
        error_type: Optional[str] = None,
        validator_ip: Optional[str] = None,
        cache_hit: bool = False,
        vector_recall: bool = False,
        mutation_detected: bool = False,
        task_url: Optional[str] = None,
        task_prompt: Optional[str] = None
    ):
        """Record a request with full metrics - ONLY records validator requests (filters localhost)"""
        # Only record if this is a validator request (not localhost)
        # This ensures metrics only reflect actual validator activity
        if not validator_ip or validator_ip in ["127.0.0.1", "localhost", "::1"]:
            return  # Skip localhost requests
        
        # Also filter out internal IPs
        if validator_ip.startswith("192.168.") or validator_ip.startswith("10.") or validator_ip.startswith("172.16."):
            return  # Skip internal IPs
        
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_types[error_type] += 1
                self.recent_errors.append({
                    "time": datetime.now().isoformat(),
                    "type": error_type,
                    "task_type": task_type
                })
        
        # Response time tracking
        self.response_times.append(response_time)
        if self.response_times:
            sorted_times = sorted(self.response_times)
            self.avg_response_time = sum(sorted_times) / len(sorted_times)
            if len(sorted_times) >= 20:
                self.p95_response_time = sorted_times[int(len(sorted_times) * 0.95)]
                self.p99_response_time = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Task type stats
        self.task_type_stats[task_type]["total"] += 1
        if success:
            self.task_type_stats[task_type]["success"] += 1
        
        # Agent performance
        if agent_type in self.agent_performance:
            self.agent_performance[agent_type]["total"] += 1
            if success:
                self.agent_performance[agent_type]["success"] += 1
            # Update average time
            agent = self.agent_performance[agent_type]
            current_avg = agent["avg_time"]
            total = agent["total"]
            agent["avg_time"] = ((current_avg * (total - 1)) + response_time) / total
        
        # Validator tracking - ONLY track if validator_ip is provided (filters out localhost)
        if validator_ip and validator_ip not in ["127.0.0.1", "localhost", "::1"]:
            # Also filter out internal IPs
            if not validator_ip.startswith("192.168.") and not validator_ip.startswith("10.") and not validator_ip.startswith("172.16."):
                self.validator_ips[validator_ip] += 1
                # Store more detailed information for historical log
                activity_entry = {
                    "time": datetime.now().isoformat(),
                    "ip": validator_ip,
                    "success": success,
                    "response_time": response_time,
                    "task_type": task_type,
                    "task_url": task_url or "",
                    "task_prompt": (task_prompt[:200] if task_prompt else ""),  # Store first 200 chars
                    "source": "in_memory"
                }
                self.validator_activity.append(activity_entry)
        
        # Cache stats
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        # Vector memory stats
        if vector_recall:
            self.vector_memory_recalls += 1
            self.vector_memory_hits += 1
        
        # Mutation detection
        if mutation_detected:
            self.mutations_detected += 1
            if success:
                self.mutations_handled += 1
        
        # Hourly trends (sample every minute)
        current_minute = int(time.time() / 60)
        if not self.hourly_success_rate or len(self.hourly_success_rate) == 0 or \
           current_minute != int(time.time() / 60):
            success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
            self.hourly_success_rate.append({
                "time": datetime.now().isoformat(),
                "success_rate": success_rate,
                "avg_response_time": self.avg_response_time
            })
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get all metrics for dashboard"""
        uptime_seconds = time.time() - self.start_time
        uptime_hours = uptime_seconds / 3600
        
        # Calculate success rates by task type
        task_type_rates = {}
        for task_type, stats in self.task_type_stats.items():
            if stats["total"] > 0:
                task_type_rates[task_type] = {
                    "success_rate": (stats["success"] / stats["total"]) * 100,
                    "total": stats["total"],
                    "success": stats["success"]
                }
        
        # Calculate agent success rates
        agent_rates = {}
        for agent_type, perf in self.agent_performance.items():
            if perf["total"] > 0:
                agent_rates[agent_type] = {
                    "success_rate": (perf["success"] / perf["total"]) * 100,
                    "total": perf["total"],
                    "success": perf["success"],
                    "avg_response_time": perf["avg_time"]
                }
        
        # Cache hit rate
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        # Vector memory hit rate
        vector_hit_rate = (self.vector_memory_hits / self.vector_memory_recalls * 100) if self.vector_memory_recalls > 0 else 0
        
        # Mutation handling rate
        mutation_handling_rate = (self.mutations_handled / self.mutations_detected * 100) if self.mutations_detected > 0 else 0
        
        # Overall success rate
        overall_success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # Top validators
        top_validators = sorted(
            self.validator_ips.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "overview": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": round(overall_success_rate, 2),
                "uptime_hours": round(uptime_hours, 2),
            },
            "performance": {
                "avg_response_time": round(self.avg_response_time, 3),
                "p95_response_time": round(self.p95_response_time, 3),
                "p99_response_time": round(self.p99_response_time, 3),
                "requests_per_minute": round(self.total_requests / (uptime_seconds / 60), 2) if uptime_seconds > 0 else 0,
            },
            "task_types": task_type_rates,
            "agents": agent_rates,
            "caching": {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate": round(cache_hit_rate, 2),
            },
            "vector_memory": {
                "recalls": self.vector_memory_recalls,
                "hits": self.vector_memory_hits,
                "hit_rate": round(vector_hit_rate, 2),
            },
            "mutations": {
                "detected": self.mutations_detected,
                "handled": self.mutations_handled,
                "handling_rate": round(mutation_handling_rate, 2),
            },
            "errors": {
                "total_errors": self.failed_requests,
                "error_types": dict(self.error_types),
                "recent_errors": list(self.recent_errors)[-10:],  # Last 10 errors
            },
            "validators": {
                "unique_validators": len(self.validator_ips),
                "top_validators": [{"ip": ip, "requests": count} for ip, count in top_validators],
                "recent_activity": list(self.validator_activity)[-20:],  # Last 20 activities
            },
            "trends": {
                "hourly_success_rate": list(self.hourly_success_rate)[-60:],
                "hourly_response_time": list(self.hourly_response_time)[-60:],
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        if self.total_requests == 0:
            return 0.0
        
        success_rate = (self.successful_requests / self.total_requests) * 100
        response_time_score = max(0, 100 - (self.avg_response_time * 10))  # Penalize slow responses
        uptime_score = min(100, (time.time() - self.start_time) / 3600 * 10)  # Reward uptime
        
        # Weighted score
        health_score = (
            success_rate * 0.5 +  # 50% weight on success
            response_time_score * 0.3 +  # 30% weight on speed
            uptime_score * 0.2  # 20% weight on uptime
        )
        
        return round(health_score, 2)

