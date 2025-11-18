"""Multi-step task planning - decompose complex tasks and plan execution"""
from typing import Dict, Any, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class TaskPlanner:
    """
    Multi-step task planner that breaks down complex tasks into sub-tasks
    and plans optimal execution order
    """
    
    # Task connectors that indicate multi-step tasks
    CONNECTORS = [
        "and", "then", "after", "before", "first", "next", "finally",
        "also", "plus", "followed by", "subsequently"
    ]
    
    # Task dependencies (what tasks require other tasks first)
    DEPENDENCIES = {
        "edit_profile": ["login"],
        "post_comment": ["login"],
        "submit_form": ["fill_form"],
        "view_dashboard": ["login"],
        "modify_settings": ["login", "navigate_to_settings"],
    }
    
    def __init__(self):
        self.execution_history = []  # Track execution history for learning
    
    def decompose_task(self, prompt: str, url: str) -> List[Dict[str, Any]]:
        """
        Break down a complex task into sub-tasks
        
        Returns:
            List of sub-tasks, each with:
            - step_number: int
            - description: str
            - task_type: str
            - dependencies: List[str]
            - estimated_complexity: str
        """
        prompt_lower = prompt.lower()
        steps = []
        
        # Check if this is a multi-step task
        has_connectors = any(connector in prompt_lower for connector in self.CONNECTORS)
        
        if not has_connectors:
            # Single-step task
            return [{
                "step_number": 1,
                "description": prompt,
                "task_type": self._detect_task_type(prompt),
                "dependencies": [],
                "estimated_complexity": self._estimate_complexity(prompt),
                "url": url
            }]
        
        # Multi-step task - split by connectors
        # Split by connectors while preserving them for context
        parts = re.split(rf"\b({'|'.join(self.CONNECTORS)})\b", prompt_lower, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        
        # Group into steps (connector + following text)
        current_step = None
        step_num = 1
        
        for i, part in enumerate(parts):
            if part.lower() in self.CONNECTORS:
                # This is a connector, next part is the step
                continue
            else:
                # This is a step description
                step = {
                    "step_number": step_num,
                    "description": part,
                    "task_type": self._detect_task_type(part),
                    "dependencies": [],
                    "estimated_complexity": self._estimate_complexity(part),
                    "url": url
                }
                
                # Check for dependencies
                step["dependencies"] = self._detect_dependencies(step, steps)
                
                steps.append(step)
                step_num += 1
        
        # If we didn't find steps, try alternative splitting
        if not steps:
            # Try splitting by common patterns
            if " and " in prompt_lower:
                parts = prompt_lower.split(" and ")
            elif " then " in prompt_lower:
                parts = prompt_lower.split(" then ")
            elif " after " in prompt_lower:
                parts = prompt_lower.split(" after ")
            else:
                parts = [prompt]
            
            for i, part in enumerate(parts, 1):
                step = {
                    "step_number": i,
                    "description": part.strip(),
                    "task_type": self._detect_task_type(part),
                    "dependencies": [],
                    "estimated_complexity": self._estimate_complexity(part),
                    "url": url
                }
                step["dependencies"] = self._detect_dependencies(step, steps)
                steps.append(step)
        
        return steps
    
    def _detect_task_type(self, description: str) -> str:
        """Detect task type from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["login", "sign in", "authenticate"]):
            return "login"
        elif any(word in desc_lower for word in ["fill", "form", "submit", "enter"]):
            return "form"
        elif any(word in desc_lower for word in ["click", "select", "choose"]):
            return "click"
        elif any(word in desc_lower for word in ["type", "enter", "input"]):
            return "type"
        elif any(word in desc_lower for word in ["edit", "modify", "change", "update"]):
            return "modify"
        elif any(word in desc_lower for word in ["search", "find"]):
            return "search"
        elif any(word in desc_lower for word in ["navigate", "go to", "open"]):
            return "navigate"
        else:
            return "generic"
    
    def _estimate_complexity(self, description: str) -> str:
        """Estimate task complexity"""
        desc_lower = description.lower()
        
        # Count action words
        action_words = ["click", "type", "fill", "submit", "navigate", "search", "modify", "edit"]
        action_count = sum(1 for word in action_words if word in desc_lower)
        
        if action_count >= 3:
            return "high"
        elif action_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _detect_dependencies(self, step: Dict[str, Any], previous_steps: List[Dict[str, Any]]) -> List[str]:
        """Detect dependencies for a step"""
        dependencies = []
        step_type = step.get("task_type", "")
        description = step.get("description", "").lower()
        
        # Check explicit dependencies
        for dep_type, required_tasks in self.DEPENDENCIES.items():
            if dep_type in description:
                dependencies.extend(required_tasks)
        
        # Check if this step requires login
        if step_type in ["modify", "edit", "post_comment", "submit_form"]:
            # Check if login was already done in previous steps
            has_login = any(s.get("task_type") == "login" for s in previous_steps)
            if not has_login:
                dependencies.append("login")
        
        # Check if this step requires navigation
        if step_type not in ["navigate", "login"] and "navigate" not in description:
            # Might need navigation if URL is provided
            if step.get("url"):
                # Check if navigation was already done
                has_navigation = any(s.get("task_type") == "navigate" for s in previous_steps)
                if not has_navigation:
                    dependencies.append("navigate")
        
        return dependencies
    
    def plan_execution(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Plan optimal execution order for steps
        
        Returns:
            Ordered list of steps with execution plan
        """
        if not steps:
            return []
        
        if len(steps) == 1:
            return steps
        
        # Build dependency graph
        execution_order = []
        remaining_steps = steps.copy()
        completed_steps = set()
        
        # Topological sort to handle dependencies
        while remaining_steps:
            # Find steps with no unmet dependencies
            ready_steps = []
            for step in remaining_steps:
                step_id = step.get("step_number")
                dependencies = step.get("dependencies", [])
                
                # Check if all dependencies are met
                dependencies_met = True
                for dep in dependencies:
                    if dep == "login":
                        # Check if login was completed
                        if not any(s.get("task_type") == "login" for s in execution_order):
                            dependencies_met = False
                            break
                    elif dep == "navigate":
                        # Check if navigation was completed
                        if not any(s.get("task_type") == "navigate" for s in execution_order):
                            dependencies_met = False
                            break
                
                if dependencies_met:
                    ready_steps.append(step)
            
            if not ready_steps:
                # No ready steps - execute remaining in order (circular dependency)
                ready_steps = [remaining_steps[0]]
            
            # Execute ready steps (in order if multiple)
            ready_steps.sort(key=lambda s: s.get("step_number", 0))
            for step in ready_steps:
                execution_order.append(step)
                completed_steps.add(step.get("step_number"))
                remaining_steps.remove(step)
        
        return execution_order
    
    def generate_execution_plan(
        self,
        prompt: str,
        url: str
    ) -> Dict[str, Any]:
        """
        Generate complete execution plan for a task
        
        Returns:
            Dict with:
            - steps: List of sub-tasks
            - execution_order: Ordered list of steps
            - total_steps: int
            - estimated_time: float (seconds)
            - has_dependencies: bool
        """
        # Decompose task
        steps = self.decompose_task(prompt, url)
        
        # Plan execution
        execution_order = self.plan_execution(steps)
        
        # Estimate total time
        estimated_time = sum(
            self._estimate_step_time(step) for step in execution_order
        )
        
        # Check for dependencies
        has_dependencies = any(
            step.get("dependencies") for step in execution_order
        )
        
        return {
            "steps": steps,
            "execution_order": execution_order,
            "total_steps": len(execution_order),
            "estimated_time": estimated_time,
            "has_dependencies": has_dependencies,
            "is_multi_step": len(steps) > 1
        }
    
    def _estimate_step_time(self, step: Dict[str, Any]) -> float:
        """Estimate time for a single step"""
        complexity = step.get("estimated_complexity", "low")
        task_type = step.get("task_type", "generic")
        
        base_times = {
            "low": 2.0,
            "medium": 5.0,
            "high": 10.0
        }
        
        base_time = base_times.get(complexity, 3.0)
        
        # Adjust for task type
        type_multipliers = {
            "login": 1.5,  # Login takes longer (redirects)
            "form": 1.2,   # Forms take longer
            "modify": 1.3, # Modifications take longer
            "navigate": 1.0,
            "click": 0.8,  # Clicks are fast
            "type": 0.7,   # Typing is fast
        }
        
        multiplier = type_multipliers.get(task_type, 1.0)
        return base_time * multiplier
    
    def track_execution(self, step: Dict[str, Any], success: bool, actual_time: float):
        """Track execution for learning"""
        self.execution_history.append({
            "step": step,
            "success": success,
            "actual_time": actual_time,
            "estimated_time": self._estimate_step_time(step)
        })
        
        # Keep only last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history.pop(0)


# Global instance
task_planner = TaskPlanner()

