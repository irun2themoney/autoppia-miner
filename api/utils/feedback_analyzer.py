"""
Feedback Analyzer - Analyzes validator/playground feedback to improve miner

This module:
1. Analyzes execution results from playground/validators
2. Identifies patterns in failures
3. Suggests improvements to action generation
4. Learns from successful executions
"""

import logging
import re
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeedbackAnalyzer:
    """
    Analyzes feedback to identify improvement opportunities
    """
    
    def __init__(self):
        self.failure_patterns = defaultdict(int)
        self.success_patterns = defaultdict(int)
        self.selector_failures = defaultdict(list)
        self.action_failures = defaultdict(list)
    
    def analyze_execution_result(
        self,
        task_id: str,
        actions: List[Dict[str, Any]],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze execution result and extract learning insights
        
        Args:
            task_id: Task identifier
            actions: Actions that were executed
            result: Execution result from playground/validator
            
        Returns:
            Analysis results with improvement suggestions
        """
        analysis = {
            "success": result.get("success", 0) > 0,
            "issues": [],
            "suggestions": [],
            "selector_issues": [],
            "action_issues": [],
        }
        
        # Analyze success/failure
        if not analysis["success"]:
            analysis["issues"].append("Task execution failed")
            
            # Analyze which actions failed
            for i, action in enumerate(actions):
                action_type = action.get("type", "Unknown")
                
                # Check for common failure patterns
                if action_type == "ClickAction":
                    if "selector" in action:
                        selector = action["selector"]
                        selector_type = selector.get("type", "unknown")
                        
                        # Check if selector might be invalid
                        value = selector.get("value", "")
                        if not value or len(value) == 0:
                            analysis["selector_issues"].append({
                                "action_index": i,
                                "issue": "Empty selector value",
                                "selector": selector,
                            })
                        
                        # Record selector failure pattern
                        self.selector_failures[selector_type].append({
                            "value": value,
                            "action": action,
                        })
                
                elif action_type == "TypeAction":
                    if "text" not in action:
                        analysis["action_issues"].append({
                            "action_index": i,
                            "issue": "Missing text field",
                            "action": action,
                        })
                
                elif action_type == "WaitAction":
                    if "timeSeconds" not in action:
                        analysis["action_issues"].append({
                            "action_index": i,
                            "issue": "Missing timeSeconds field",
                            "action": action,
                        })
        
        # Generate suggestions
        if analysis["selector_issues"]:
            analysis["suggestions"].append(
                "Improve selector generation - ensure all selectors have non-empty values"
            )
        
        if analysis["action_issues"]:
            analysis["suggestions"].append(
                "Fix action generation - ensure all required fields are present"
            )
        
        # Record patterns
        if analysis["success"]:
            self.success_patterns[task_id] += 1
        else:
            self.failure_patterns[task_id] += 1
        
        return analysis
    
    def get_improvement_suggestions(self) -> List[str]:
        """Get improvement suggestions based on analyzed failures"""
        suggestions = []
        
        # Analyze selector failures
        if self.selector_failures:
            most_failed_type = max(
                self.selector_failures.items(),
                key=lambda x: len(x[1])
            )
            suggestions.append(
                f"Selector type '{most_failed_type[0]}' has {len(most_failed_type[1])} failures - "
                f"consider improving selector generation for this type"
            )
        
        # Analyze action failures
        if self.action_failures:
            most_failed_action = max(
                self.action_failures.items(),
                key=lambda x: len(x[1])
            )
            suggestions.append(
                f"Action type '{most_failed_action[0]}' has {len(most_failed_action[1])} failures - "
                f"review action generation logic"
            )
        
        return suggestions
    
    def analyze_empty_actions_issue(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze why actions might be empty in response
        
        Args:
            response_data: Response data that should contain actions
            
        Returns:
            Analysis of empty actions issue
        """
        analysis = {
            "has_actions": "actions" in response_data,
            "actions_count": len(response_data.get("actions", [])),
            "possible_causes": [],
            "fixes": [],
        }
        
        if not analysis["has_actions"]:
            analysis["possible_causes"].append("Response missing 'actions' field")
            analysis["fixes"].append("Ensure response always includes 'actions' field")
        
        elif analysis["actions_count"] == 0:
            analysis["possible_causes"].append("Actions array is empty")
            analysis["fixes"].append("Ensure actions array is never empty - use fallback actions")
        
        # Check response format
        if "webAgentId" not in response_data:
            analysis["possible_causes"].append("Missing webAgentId field (camelCase)")
            analysis["fixes"].append("Add webAgentId field to response")
        
        if "recording" not in response_data:
            analysis["possible_causes"].append("Missing recording field")
            analysis["fixes"].append("Add recording field (can be empty string)")
        
        return analysis


# Global feedback analyzer instance
_feedback_analyzer: Optional[FeedbackAnalyzer] = None


def get_feedback_analyzer() -> FeedbackAnalyzer:
    """Get or create global feedback analyzer instance"""
    global _feedback_analyzer
    if _feedback_analyzer is None:
        _feedback_analyzer = FeedbackAnalyzer()
    return _feedback_analyzer

