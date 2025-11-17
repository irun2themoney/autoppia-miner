"""Advanced action optimization"""
from typing import Dict, Any, List


class ActionOptimizer:
    """Optimize action sequences for maximum efficiency"""
    
    def optimize(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all optimizations"""
        optimized = actions.copy()
        
        # Remove redundant actions
        optimized = self._remove_redundant(optimized)
        
        # Merge similar actions
        optimized = self._merge_similar(optimized)
        
        # Optimize wait times
        optimized = self._optimize_waits(optimized)
        
        # Ensure proper ordering
        optimized = self._ensure_ordering(optimized)
        
        return optimized
    
    def _remove_redundant(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove redundant actions"""
        if not actions:
            return actions
        
        optimized = []
        prev_action = None
        
        for action in actions:
            action_type = action.get("type", "")
            
            # Skip duplicate consecutive screenshots
            if action_type == "ScreenshotAction":
                if prev_action and prev_action.get("type") == "ScreenshotAction":
                    continue
            
            # Skip duplicate navigations
            if action_type == "NavigateAction":
                if prev_action and prev_action.get("type") == "NavigateAction":
                    # Keep the latest navigation
                    optimized.pop()
            
            optimized.append(action)
            prev_action = action
        
        return optimized
    
    def _merge_similar(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge similar consecutive actions"""
        if len(actions) < 2:
            return actions
        
        optimized = []
        i = 0
        
        while i < len(actions):
            current = actions[i]
            current_type = current.get("type", "")
            
            # Merge consecutive wait actions
            if current_type == "WaitAction":
                total_wait = current.get("time_seconds", 0)
                j = i + 1
                while j < len(actions) and actions[j].get("type") == "WaitAction":
                    total_wait += actions[j].get("time_seconds", 0)
                    j += 1
                
                # Cap at reasonable maximum
                total_wait = min(total_wait, 5.0)
                
                if total_wait > 0:
                    optimized.append({
                        "type": "WaitAction",
                        "time_seconds": total_wait
                    })
                
                i = j
                continue
            
            optimized.append(current)
            i += 1
        
        return optimized
    
    def _optimize_waits(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize wait times"""
        optimized = []
        
        for action in actions:
            if action.get("type") == "WaitAction":
                time_seconds = action.get("time_seconds", 0)
                # Remove very short waits (< 0.1s)
                if time_seconds < 0.1:
                    continue
                # Cap excessive waits
                if time_seconds > 5.0:
                    action["time_seconds"] = 5.0
            
            optimized.append(action)
        
        return optimized
    
    def _ensure_ordering(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure actions are in proper order"""
        if not actions:
            return actions
        
        # Find navigation action
        nav_action = None
        nav_index = -1
        
        for i, action in enumerate(actions):
            if action.get("type") == "NavigateAction":
                nav_action = action
                nav_index = i
                break
        
        # Move navigation to front if not already
        if nav_action and nav_index > 0:
            actions = [nav_action] + [a for i, a in enumerate(actions) if i != nav_index]
        
        return actions

