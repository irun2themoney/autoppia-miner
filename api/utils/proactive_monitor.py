"""Proactive monitoring and alerting system for miner health"""
import asyncio
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class ProactiveMonitor:
    """
    Proactive monitoring system that:
    - Tracks miner health metrics
    - Detects issues before they become problems
    - Provides alerts and recommendations
    - Monitors validator activity patterns
    """
    
    def __init__(self):
        self.health_checks = deque(maxlen=1000)
        self.validator_activity_window = deque(maxlen=100)
        self.last_validator_activity = None
        self.consecutive_no_activity = 0
        self.health_score = 100.0
        
        # Alert thresholds
        self.max_no_activity_hours = 24  # Alert if no activity for 24 hours
        self.min_health_score = 70.0  # Alert if health drops below 70
        
        # Performance tracking
        self.response_time_trend = deque(maxlen=50)
        self.success_rate_trend = deque(maxlen=50)
        
    def record_health_check(self, metrics: Dict[str, Any]):
        """Record a health check with current metrics"""
        check = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "health_score": self._calculate_health_score(metrics)
        }
        self.health_checks.append(check)
        self.health_score = check["health_score"]
        
        # Track trends
        if "avg_response_time" in metrics:
            self.response_time_trend.append(metrics["avg_response_time"])
        if "success_rate" in metrics:
            self.success_rate_trend.append(metrics["success_rate"])
        
        # Check for alerts
        self._check_alerts(metrics)
    
    def record_validator_activity(self, validator_ip: str, success: bool):
        """Record validator activity"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "validator_ip": validator_ip,
            "success": success
        }
        self.validator_activity_window.append(activity)
        self.last_validator_activity = datetime.now()
        self.consecutive_no_activity = 0
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0
        
        # API uptime (30% weight)
        uptime_hours = metrics.get("uptime_hours", 0)
        if uptime_hours < 1:
            score -= 10  # Very new, slight penalty
        elif uptime_hours > 168:  # 1 week+
            score += 5  # Bonus for stability
        
        # Response time (25% weight)
        avg_response_time = metrics.get("avg_response_time", 0)
        if avg_response_time > 5.0:
            score -= 15  # Too slow
        elif avg_response_time > 2.0:
            score -= 5  # Slightly slow
        elif avg_response_time < 1.0:
            score += 5  # Fast
        
        # Success rate (25% weight)
        success_rate = metrics.get("success_rate", 0)
        if success_rate < 0.5:
            score -= 20  # Poor success rate
        elif success_rate < 0.7:
            score -= 10  # Below average
        elif success_rate > 0.85:
            score += 10  # Excellent
        
        # Validator activity (20% weight)
        hours_since_activity = self._hours_since_last_activity()
        if hours_since_activity > 48:
            score -= 20  # No activity for 2+ days
        elif hours_since_activity > 24:
            score -= 10  # No activity for 1+ day
        elif hours_since_activity < 1:
            score += 10  # Recent activity
        
        return max(0.0, min(100.0, score))
    
    def _hours_since_last_activity(self) -> float:
        """Calculate hours since last validator activity"""
        if not self.last_validator_activity:
            # Check if we have any activity in window
            if len(self.validator_activity_window) > 0:
                last = self.validator_activity_window[-1]
                last_time = datetime.fromisoformat(last["timestamp"])
                return (datetime.now() - last_time).total_seconds() / 3600
            return 999.0  # No activity ever
        
        return (datetime.now() - self.last_validator_activity).total_seconds() / 3600
    
    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for issues and log alerts"""
        hours_since_activity = self._hours_since_last_activity()
        
        # Alert: No validator activity
        if hours_since_activity > self.max_no_activity_hours:
            self.consecutive_no_activity += 1
            if self.consecutive_no_activity == 1:  # Only log once per day
                logger.warning(
                    f"⚠️  ALERT: No validator activity for {hours_since_activity:.1f} hours. "
                    f"Miner is healthy but waiting for validators to test."
                )
        
        # Alert: Health score low
        if self.health_score < self.min_health_score:
            logger.warning(
                f"⚠️  ALERT: Health score is {self.health_score:.1f}/100. "
                f"Check metrics: {metrics}"
            )
        
        # Alert: Response time increasing
        if len(self.response_time_trend) >= 10:
            recent_avg = sum(list(self.response_time_trend)[-5:]) / 5
            older_avg = sum(list(self.response_time_trend)[-10:-5]) / 5
            if recent_avg > older_avg * 1.5:  # 50% increase
                logger.warning(
                    f"⚠️  ALERT: Response time increasing. "
                    f"Recent: {recent_avg:.2f}s, Previous: {older_avg:.2f}s"
                )
        
        # Alert: Success rate decreasing
        if len(self.success_rate_trend) >= 10:
            recent_avg = sum(list(self.success_rate_trend)[-5:]) / 5
            older_avg = sum(list(self.success_rate_trend)[-10:-5]) / 5
            if recent_avg < older_avg * 0.8:  # 20% decrease
                logger.warning(
                    f"⚠️  ALERT: Success rate decreasing. "
                    f"Recent: {recent_avg:.2%}, Previous: {older_avg:.2%}"
                )
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        hours_since_activity = self._hours_since_last_activity()
        
        # Calculate trends
        response_trend = "stable"
        if len(self.response_time_trend) >= 5:
            recent = sum(list(self.response_time_trend)[-3:]) / 3
            older = sum(list(self.response_time_trend)[-5:-3]) / 2
            if recent > older * 1.2:
                response_trend = "increasing"
            elif recent < older * 0.8:
                response_trend = "decreasing"
        
        success_trend = "stable"
        if len(self.success_rate_trend) >= 5:
            recent = sum(list(self.success_rate_trend)[-3:]) / 3
            older = sum(list(self.success_rate_trend)[-5:-3]) / 2
            if recent > older * 1.1:
                success_trend = "improving"
            elif recent < older * 0.9:
                success_trend = "declining"
        
        return {
            "health_score": round(self.health_score, 2),
            "status": self._get_status(),
            "hours_since_last_activity": round(hours_since_activity, 2),
            "total_health_checks": len(self.health_checks),
            "recent_validator_activity": len(self.validator_activity_window),
            "response_time_trend": response_trend,
            "success_rate_trend": success_trend,
            "alerts": self._get_active_alerts(),
            "recommendations": self._get_recommendations()
        }
    
    def _get_status(self) -> str:
        """Get overall status"""
        if self.health_score >= 90:
            return "excellent"
        elif self.health_score >= 75:
            return "good"
        elif self.health_score >= 60:
            return "fair"
        else:
            return "needs_attention"
    
    def _get_active_alerts(self) -> list:
        """Get list of active alerts"""
        alerts = []
        hours_since_activity = self._hours_since_last_activity()
        
        if hours_since_activity > self.max_no_activity_hours:
            alerts.append({
                "type": "no_validator_activity",
                "severity": "medium",
                "message": f"No validator activity for {hours_since_activity:.1f} hours",
                "recommendation": "Monitor for validator tests. Miner is ready and waiting."
            })
        
        if self.health_score < self.min_health_score:
            alerts.append({
                "type": "low_health_score",
                "severity": "high",
                "message": f"Health score is {self.health_score:.1f}/100",
                "recommendation": "Check metrics and logs for issues"
            })
        
        return alerts
    
    def _get_recommendations(self) -> list:
        """Get actionable recommendations"""
        recommendations = []
        hours_since_activity = self._hours_since_last_activity()
        
        if hours_since_activity > 48:
            recommendations.append({
                "priority": "high",
                "action": "Wait for validator tests",
                "reason": "No activity for 2+ days. Validators test in cycles."
            })
        elif hours_since_activity > 24:
            recommendations.append({
                "priority": "medium",
                "action": "Monitor for validator tests",
                "reason": "No recent activity. Miner is ready and waiting."
            })
        
        if self.health_score < 80:
            recommendations.append({
                "priority": "medium",
                "action": "Review performance metrics",
                "reason": "Health score below optimal. Check response times and success rates."
            })
        
        if len(self.response_time_trend) >= 5:
            recent_avg = sum(list(self.response_time_trend)[-3:]) / 3
            if recent_avg > 3.0:
                recommendations.append({
                    "priority": "low",
                    "action": "Optimize response times",
                    "reason": f"Average response time is {recent_avg:.2f}s (target: <2s)"
                })
        
        return recommendations


# Global instance
proactive_monitor = ProactiveMonitor()

