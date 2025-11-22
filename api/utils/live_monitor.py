"""
Live Monitor - Real-time activity tracking for live dashboard
Tracks every task, action, and validator interaction in real-time
"""
import time
import logging
from collections import deque
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LiveMonitor:
    """Track live activity for real-time monitoring"""
    
    def __init__(self, max_events: int = 1000):
        self.max_events = max_events
        self.events = deque(maxlen=max_events)  # Recent events
        self.active_tasks = {}  # task_id -> task_info
        self.task_history = deque(maxlen=500)  # Completed tasks
        self.validator_activity = deque(maxlen=200)  # Recent validator interactions
        
    def log_task_start(self, task_id: str, prompt: str, url: str, validator_ip: Optional[str] = None):
        """Log when a task starts processing"""
        event = {
            "type": "task_start",
            "task_id": task_id,
            "prompt": prompt[:100] if prompt else "",  # First 100 chars
            "url": url,
            "validator_ip": validator_ip,
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        self.active_tasks[task_id] = {
            "task_id": task_id,
            "prompt": prompt,
            "url": url,
            "validator_ip": validator_ip,
            "start_time": time.time(),
            "status": "processing",
            "actions_generated": 0,
            "current_step": "initializing"
        }
        logger.info(f"📥 Task started: {task_id} from {validator_ip or 'unknown'}")
    
    def log_task_step(self, task_id: str, step: str, details: Optional[Dict[str, Any]] = None):
        """Log a step in task processing"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["current_step"] = step
            if details:
                self.active_tasks[task_id].update(details)
        
        event = {
            "type": "task_step",
            "task_id": task_id,
            "step": step,
            "details": details or {},
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.debug(f"📊 Task step: {task_id} - {step}")
    
    def log_action_generated(self, task_id: str, action_count: int, action_type: Optional[str] = None):
        """Log when actions are generated"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["actions_generated"] = action_count
            self.active_tasks[task_id]["current_step"] = f"generated {action_count} actions"
        
        event = {
            "type": "actions_generated",
            "task_id": task_id,
            "action_count": action_count,
            "action_type": action_type,
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.info(f"✅ Actions generated: {task_id} - {action_count} actions")
    
    def log_task_complete(self, task_id: str, success: bool, action_count: int, 
                         response_time: float, error: Optional[str] = None):
        """Log when a task completes"""
        task_info = self.active_tasks.pop(task_id, {})
        
        completed_task = {
            "task_id": task_id,
            "prompt": task_info.get("prompt", ""),
            "url": task_info.get("url", ""),
            "validator_ip": task_info.get("validator_ip"),
            "success": success,
            "action_count": action_count,
            "response_time": response_time,
            "error": error,
            "start_time": task_info.get("start_time", time.time()),
            "end_time": time.time(),
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        
        self.task_history.append(completed_task)
        
        event = {
            "type": "task_complete",
            "task_id": task_id,
            "success": success,
            "action_count": action_count,
            "response_time": response_time,
            "error": error,
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        
        # Also log to validator activity
        if task_info.get("validator_ip"):
            self.validator_activity.append({
                "validator_ip": task_info["validator_ip"],
                "task_id": task_id,
                "success": success,
                "response_time": response_time,
                "timestamp": time.time(),
                "time_str": datetime.now().isoformat()
            })
        
        status_emoji = "✅" if success else "❌"
        logger.info(f"{status_emoji} Task complete: {task_id} - {action_count} actions in {response_time:.2f}s")
    
    def log_validator_connection(self, validator_ip: str, endpoint: str):
        """Log when a validator connects"""
        event = {
            "type": "validator_connection",
            "validator_ip": validator_ip,
            "endpoint": endpoint,
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.info(f"🔗 Validator connected: {validator_ip} - {endpoint}")
    
    def log_cache_hit(self, task_id: str, cache_type: str):
        """Log when cache is used"""
        event = {
            "type": "cache_hit",
            "task_id": task_id,
            "cache_type": cache_type,
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.debug(f"💾 Cache hit: {task_id} - {cache_type}")
    
    def log_error(self, task_id: str, error_type: str, error_message: str):
        """Log errors"""
        event = {
            "type": "error",
            "task_id": task_id,
            "error_type": error_type,
            "error_message": error_message[:200],  # First 200 chars
            "timestamp": time.time(),
            "time_str": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.error(f"❌ Error: {task_id} - {error_type}: {error_message[:100]}")
    
    def get_recent_events(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent events, optionally filtered by type"""
        events = list(self.events)
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        return events[-limit:]
    
    def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active tasks"""
        # Clean up stale tasks (older than 5 minutes)
        current_time = time.time()
        stale_tasks = [
            task_id for task_id, task_info in self.active_tasks.items()
            if current_time - task_info.get("start_time", 0) > 300  # 5 minutes
        ]
        for task_id in stale_tasks:
            del self.active_tasks[task_id]
        
        return dict(self.active_tasks)
    
    def get_live_status(self) -> Dict[str, Any]:
        """Get current live status"""
        active_tasks = self.get_active_tasks()
        recent_events = self.get_recent_events(50)
        recent_validator_activity = list(self.validator_activity)[-20:]
        
        return {
            "active_tasks": active_tasks,
            "active_task_count": len(active_tasks),
            "recent_events": recent_events,
            "recent_validator_activity": recent_validator_activity,
            "total_events": len(self.events),
            "timestamp": time.time()
        }


# Global instance
live_monitor = LiveMonitor()

