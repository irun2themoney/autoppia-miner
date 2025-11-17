"""Smart action sequencing and optimization"""
from typing import Dict, Any, List


class ActionSequencer:
    """Optimize action sequences for better execution"""
    
    def optimize_sequence(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize action sequence"""
        if not actions:
            return actions
        
        optimized = []
        prev_action = None
        
        for action in actions:
            action_type = action.get("type", "")
            
            # Remove redundant screenshots (don't screenshot twice in a row)
            if action_type == "ScreenshotAction":
                if prev_action and prev_action.get("type") == "ScreenshotAction":
                    continue  # Skip duplicate screenshot
            
            # Optimize wait times
            if action_type == "WaitAction":
                time_seconds = action.get("time_seconds", 0)
                # Cap wait times
                if time_seconds > 5:
                    action["time_seconds"] = 5.0
                # Remove very short waits (< 0.1s)
                if time_seconds < 0.1:
                    continue
            
            # Ensure navigation comes first
            if action_type == "NavigateAction" and optimized:
                # Move navigation to front
                optimized.insert(0, action)
                prev_action = action
                continue
            
            optimized.append(action)
            prev_action = action
        
        # Ensure we have at least one screenshot if actions exist
        has_screenshot = any(a.get("type") == "ScreenshotAction" for a in optimized)
        if optimized and not has_screenshot:
            # Add screenshot after last action
            optimized.append({"type": "ScreenshotAction"})
        
        return optimized
    
    def add_smart_waits(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add smart wait times between actions"""
        if not actions:
            return actions
        
        optimized = []
        
        for i, action in enumerate(actions):
            optimized.append(action)
            
            action_type = action.get("type", "")
            next_action = actions[i + 1] if i + 1 < len(actions) else None
            
            # Add wait after navigation
            if action_type == "NavigateAction" and next_action:
                if next_action.get("type") != "WaitAction":
                    optimized.append({
                        "type": "WaitAction",
                        "time_seconds": 1.5  # Wait for page load
                    })
            
            # Add short wait after type actions
            elif action_type == "TypeAction" and next_action:
                if next_action.get("type") not in ["WaitAction", "ScreenshotAction"]:
                    optimized.append({
                        "type": "WaitAction",
                        "time_seconds": 0.3  # Short wait after typing
                    })
            
            # Add wait before click if previous was type
            elif action_type == "ClickAction" and i > 0:
                prev_action = actions[i - 1]
                if prev_action.get("type") == "TypeAction":
                    # Already added wait after type, skip
                    pass
                elif prev_action.get("type") != "WaitAction":
                    optimized.insert(-1, {
                        "type": "WaitAction",
                        "time_seconds": 0.3  # Short wait before click
                    })
        
        return optimized

