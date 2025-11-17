"""Performance optimizations for maximum speed and efficiency"""
from typing import Dict, Any, List
import time
import asyncio
from collections import deque


class PerformanceOptimizer:
    """Optimize performance for maximum speed"""
    
    def __init__(self):
        self.response_times = deque(maxlen=100)
        self.optimization_cache = {}
    
    def optimize_response_time(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize actions for faster execution"""
        optimized = actions.copy()
        
        # Remove unnecessary waits
        optimized = self._optimize_waits(optimized)
        
        # Parallelize independent actions (if possible)
        optimized = self._identify_parallel_opportunities(optimized)
        
        # Minimize screenshots (keep only essential)
        optimized = self._optimize_screenshots(optimized)
        
        return optimized
    
    def _optimize_waits(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize wait times for speed"""
        optimized = []
        
        for action in actions:
            if action.get("type") == "WaitAction":
                time_seconds = action.get("time_seconds", 0)
                
                # Reduce excessive waits
                if time_seconds > 3.0:
                    action["time_seconds"] = 3.0
                # Remove very short waits (< 0.2s) - not needed
                elif time_seconds < 0.2:
                    continue
            
            optimized.append(action)
        
        return optimized
    
    def _optimize_screenshots(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep only essential screenshots"""
        optimized = []
        screenshot_count = 0
        last_action_type = None
        
        for action in actions:
            if action.get("type") == "ScreenshotAction":
                # Keep first screenshot (after navigation)
                if screenshot_count == 0:
                    optimized.append(action)
                    screenshot_count += 1
                # Keep screenshot after important actions
                elif last_action_type in ["ClickAction", "TypeAction"]:
                    # Only if we haven't taken one recently
                    if screenshot_count < 3:  # Limit to 3 screenshots total
                        optimized.append(action)
                        screenshot_count += 1
                # Skip redundant screenshots
            else:
                optimized.append(action)
                last_action_type = action.get("type")
        
        return optimized
    
    def _identify_parallel_opportunities(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify actions that could be parallelized (for future optimization)"""
        # Note: IWA actions are sequential, but we can optimize the sequence
        # This is a placeholder for future parallel execution if supported
        return actions
    
    def track_response_time(self, response_time: float):
        """Track response time for optimization"""
        self.response_times.append(response_time)
    
    def get_avg_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def is_performance_acceptable(self, threshold: float = 2.0) -> bool:
        """Check if performance is acceptable"""
        avg_time = self.get_avg_response_time()
        return avg_time <= threshold

