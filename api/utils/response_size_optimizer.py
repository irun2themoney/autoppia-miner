"""
Response Size Optimizer - Prevents disconnections from 1MB Bittensor limit
Bittensor has a maximum response size of ~1MB. If actions exceed this, validators disconnect.
"""
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Bittensor maximum response size (conservative limit to avoid disconnections)
MAX_RESPONSE_SIZE_BYTES = 900 * 1024  # 900KB (leave 100KB buffer for other response fields)
MAX_ACTIONS_HARD_LIMIT = 200  # Hard limit on number of actions


class ResponseSizeOptimizer:
    """Optimize response size to stay under Bittensor's 1MB limit"""
    
    def __init__(self):
        self.max_size = MAX_RESPONSE_SIZE_BYTES
        self.max_actions = MAX_ACTIONS_HARD_LIMIT
    
    def get_response_size(self, actions: List[Dict[str, Any]], extra_fields: Dict[str, Any] = None) -> int:
        """Calculate the size of the full response in bytes"""
        response = {
            "actions": actions,
            "web_agent_id": extra_fields.get("web_agent_id", "") if extra_fields else "",
            "recording": extra_fields.get("recording", "") if extra_fields else "",
            "id": extra_fields.get("id", "") if extra_fields else "",
            "task_id": extra_fields.get("task_id", "") if extra_fields else "",
        }
        json_str = json.dumps(response, separators=(',', ':'))  # Compact JSON
        return len(json_str.encode('utf-8'))
    
    def optimize_actions(self, actions: List[Dict[str, Any]], extra_fields: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Optimize actions to stay under size limit.
        Returns optimized actions that fit within the size limit.
        CRITICAL: NEVER returns empty array - always returns at least one action.
        """
        if not actions:
            # CRITICAL: Never return empty - return at least one action
            logger.warning("optimize_actions called with empty actions, returning fallback")
            return [{"type": "ScreenshotAction"}]
        
        # Step 1: Hard limit on action count (prevent excessive actions)
        if len(actions) > self.max_actions:
            logger.warning(f"Action count ({len(actions)}) exceeds hard limit ({self.max_actions}). Truncating.")
            actions = actions[:self.max_actions]
        
        # Step 2: Check initial size
        current_size = self.get_response_size(actions, extra_fields)
        
        if current_size <= self.max_size:
            # Already under limit, return as-is
            return actions
        
        logger.warning(f"Response size ({current_size / 1024:.1f}KB) exceeds limit ({self.max_size / 1024:.1f}KB). Optimizing...")
        
        # Step 3: Remove non-essential fields from actions
        optimized = self._remove_non_essential_fields(actions)
        current_size = self.get_response_size(optimized, extra_fields)
        
        if current_size <= self.max_size:
            logger.info(f"Optimized by removing non-essential fields. New size: {current_size / 1024:.1f}KB")
            return optimized
        
        # Step 4: Remove redundant screenshots (keep only essential ones)
        optimized = self._remove_redundant_screenshots(optimized)
        current_size = self.get_response_size(optimized, extra_fields)
        
        if current_size <= self.max_size:
            logger.info(f"Optimized by removing redundant screenshots. New size: {current_size / 1024:.1f}KB")
            return optimized
        
        # Step 5: Truncate selectors (keep only essential selector info)
        optimized = self._truncate_selectors(optimized)
        current_size = self.get_response_size(optimized, extra_fields)
        
        if current_size <= self.max_size:
            logger.info(f"Optimized by truncating selectors. New size: {current_size / 1024:.1f}KB")
            return optimized
        
        # Step 6: Remove less critical actions (keep core task actions)
        optimized = self._prioritize_core_actions(optimized)
        current_size = self.get_response_size(optimized, extra_fields)
        
        if current_size <= self.max_size:
            logger.info(f"Optimized by prioritizing core actions. New size: {current_size / 1024:.1f}KB")
            return optimized
        
        # Step 7: Binary search to find maximum actions that fit
        optimized = self._binary_search_optimal_size(actions, extra_fields)
        final_size = self.get_response_size(optimized, extra_fields)
        
        logger.warning(f"Final optimized size: {final_size / 1024:.1f}KB ({len(optimized)} actions, reduced from {len(actions)})")
        
        return optimized
    
    def _remove_non_essential_fields(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove non-essential fields from actions to reduce size"""
        optimized = []
        essential_fields = {"action_type", "action", "type", "selector", "url", "text", "value", "duration", "time_seconds", "direction"}
        
        for action in actions:
            optimized_action = {}
            for key, value in action.items():
                if key in essential_fields or key.startswith("_"):  # Keep essential fields and internal fields
                    optimized_action[key] = value
            optimized.append(optimized_action)
        
        return optimized
    
    def _remove_redundant_screenshots(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove redundant screenshot actions (keep only essential ones)"""
        optimized = []
        screenshot_count = 0
        max_screenshots = 10  # Limit total screenshots
        
        for i, action in enumerate(actions):
            action_type = action.get("action_type") or action.get("type", "")
            
            # Skip redundant screenshots
            if action_type in ["screenshot", "ScreenshotAction"]:
                screenshot_count += 1
                # Keep first screenshot, last screenshot, and every 5th screenshot
                if screenshot_count == 1 or screenshot_count % 5 == 0 or i == len(actions) - 1:
                    optimized.append(action)
                elif screenshot_count > max_screenshots:
                    continue  # Skip this screenshot
                else:
                    optimized.append(action)
            else:
                optimized.append(action)
        
        return optimized
    
    def _truncate_selectors(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Truncate selector values to reduce size"""
        optimized = []
        
        for action in actions:
            optimized_action = action.copy()
            selector = action.get("selector")
            
            if selector and isinstance(selector, dict):
                # Keep only essential selector fields
                truncated_selector = {}
                for key in ["type", "value"]:  # Only keep type and value
                    if key in selector:
                        value = selector[key]
                        # Truncate long selector values
                        if isinstance(value, str) and len(value) > 200:
                            truncated_selector[key] = value[:200]
                        else:
                            truncated_selector[key] = value
                optimized_action["selector"] = truncated_selector
            
            optimized.append(optimized_action)
        
        return optimized
    
    def _prioritize_core_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep only core task actions, remove less critical ones"""
        # Priority order: navigate > click > type > wait > screenshot
        priority_map = {
            "navigate": 5,
            "goto": 5,
            "click": 4,
            "type": 4,
            "scroll": 3,
            "wait": 2,
            "screenshot": 1,
        }
        
        # Score each action
        scored_actions = []
        for i, action in enumerate(actions):
            action_type = action.get("action_type") or action.get("type", "")
            priority = priority_map.get(action_type.lower(), 0)
            # Boost priority for first and last actions
            if i == 0 or i == len(actions) - 1:
                priority += 2
            scored_actions.append((priority, i, action))
        
        # Sort by priority (descending) and take top actions
        scored_actions.sort(reverse=True, key=lambda x: x[0])
        
        # Keep top 80% of actions by priority
        keep_count = max(10, int(len(actions) * 0.8))
        kept_indices = set(i for _, i, _ in scored_actions[:keep_count])
        
        # Return actions in original order, but only kept ones
        optimized = [action for i, action in enumerate(actions) if i in kept_indices]
        
        return optimized
    
    def _binary_search_optimal_size(self, actions: List[Dict[str, Any]], extra_fields: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Binary search to find maximum number of actions that fit within size limit"""
        # Start with optimized actions
        optimized = self._remove_non_essential_fields(actions)
        optimized = self._remove_redundant_screenshots(optimized)
        optimized = self._truncate_selectors(optimized)
        
        # Binary search for optimal count
        left = 1
        right = len(optimized)
        best = []
        
        while left <= right:
            mid = (left + right) // 2
            test_actions = optimized[:mid]
            size = self.get_response_size(test_actions, extra_fields)
            
            if size <= self.max_size:
                best = test_actions
                left = mid + 1  # Try more actions
            else:
                right = mid - 1  # Try fewer actions
        
        # CRITICAL: Never return empty - always return at least one action
        result = best if best else optimized[:1] if optimized else [{"type": "ScreenshotAction"}]
        if not result or len(result) == 0:
            logger.error("Binary search returned empty, using fallback")
            result = [{"type": "ScreenshotAction"}]
        return result


# Global instance
response_size_optimizer = ResponseSizeOptimizer()

