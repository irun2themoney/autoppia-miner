"""
Empty Actions Diagnostic Tool

This module provides comprehensive diagnostics for the empty actions issue.
It tracks response generation at every step to identify where actions become empty.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class EmptyActionsDiagnostic:
    """
    Diagnostic tool to track and identify empty actions issues
    """
    
    def __init__(self):
        self.checkpoints = []
        self.empty_actions_events = []
    
    def checkpoint(
        self,
        stage: str,
        task_id: str,
        actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Record a checkpoint in the action generation pipeline
        
        Args:
            stage: Stage name (e.g., "agent_returned", "after_conversion", "before_response")
            task_id: Task identifier
            actions: Actions at this stage
            context: Additional context (optional)
        """
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "task_id": task_id,
            "actions_count": len(actions) if actions else 0,
            "actions_empty": not actions or len(actions) == 0,
            "context": context or {},
        }
        
        self.checkpoints.append(checkpoint)
        
        # If actions are empty at this stage, record it
        if checkpoint["actions_empty"]:
            self.empty_actions_events.append({
                **checkpoint,
                "actions": actions,
            })
            logger.error(
                f"🚨 EMPTY ACTIONS DETECTED at stage '{stage}' for task {task_id}"
            )
        
        # Keep only last 100 checkpoints
        if len(self.checkpoints) > 100:
            self.checkpoints = self.checkpoints[-100:]
        
        # Keep only last 50 empty events
        if len(self.empty_actions_events) > 50:
            self.empty_actions_events = self.empty_actions_events[-50:]
    
    def validate_response_before_send(
        self,
        task_id: str,
        response_content: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate response before sending to ensure actions are not empty
        
        Args:
            task_id: Task identifier
            response_content: Response content dictionary
            
        Returns:
            (is_valid, error_message)
        """
        # Check if actions field exists
        if "actions" not in response_content:
            return False, "Response missing 'actions' field"
        
        actions = response_content["actions"]
        
        # Check if actions is a list
        if not isinstance(actions, list):
            return False, f"Actions is not a list: {type(actions)}"
        
        # Check if actions is empty
        if len(actions) == 0:
            return False, "Actions array is empty"
        
        # Validate JSON serialization
        try:
            json_str = json.dumps(response_content)
            # Check if serialized JSON contains empty actions
            if '"actions":[]' in json_str or '"actions": []' in json_str:
                return False, "JSON serialization shows empty actions array"
        except Exception as e:
            return False, f"JSON serialization failed: {e}"
        
        return True, None
    
    def get_diagnostic_report(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get diagnostic report for empty actions issues
        
        Args:
            task_id: Optional task ID to filter by
            
        Returns:
            Diagnostic report
        """
        if task_id:
            relevant_checkpoints = [
                c for c in self.checkpoints if c["task_id"] == task_id
            ]
            relevant_events = [
                e for e in self.empty_actions_events if e["task_id"] == task_id
            ]
        else:
            relevant_checkpoints = self.checkpoints
            relevant_events = self.empty_actions_events
        
        # Analyze empty actions events
        stage_analysis = {}
        for event in relevant_events:
            stage = event["stage"]
            if stage not in stage_analysis:
                stage_analysis[stage] = {
                    "count": 0,
                    "tasks": [],
                }
            stage_analysis[stage]["count"] += 1
            stage_analysis[stage]["tasks"].append(event["task_id"])
        
        return {
            "total_checkpoints": len(relevant_checkpoints),
            "empty_actions_events": len(relevant_events),
            "stage_analysis": stage_analysis,
            "recent_empty_events": relevant_events[-10:] if relevant_events else [],
            "recent_checkpoints": relevant_checkpoints[-20:] if relevant_checkpoints else [],
        }
    
    def trace_action_flow(
        self,
        task_id: str,
        stages: List[Tuple[str, List[Dict[str, Any]]]]
    ):
        """
        Trace action flow through multiple stages
        
        Args:
            task_id: Task identifier
            stages: List of (stage_name, actions) tuples
        """
        logger.info(f"🔍 Tracing action flow for task {task_id}")
        
        for stage_name, actions in stages:
            self.checkpoint(stage_name, task_id, actions)
            logger.debug(
                f"  Stage '{stage_name}': {len(actions) if actions else 0} actions"
            )
        
        # Check if actions were lost at any stage
        action_counts = [len(actions) if actions else 0 for _, actions in stages]
        if any(count == 0 for count in action_counts):
            logger.error(
                f"🚨 Actions became empty during flow for task {task_id}: "
                f"Counts: {action_counts}"
            )


# Global diagnostic instance
_diagnostic: Optional[EmptyActionsDiagnostic] = None


def get_diagnostic() -> EmptyActionsDiagnostic:
    """Get or create global diagnostic instance"""
    global _diagnostic
    if _diagnostic is None:
        _diagnostic = EmptyActionsDiagnostic()
    return _diagnostic

