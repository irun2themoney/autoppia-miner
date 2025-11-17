"""Ensemble action generation - multiple strategies, pick best"""
from typing import Dict, Any, List, Optional
import asyncio
import logging


class EnsembleGenerator:
    """Generate actions using multiple strategies and select best"""
    
    def __init__(self):
        self.strategies = []
    
    async def generate_ensemble(
        self,
        prompt: str,
        url: str,
        strategies: List[Any],
        parsed_task: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate actions using multiple strategies in parallel"""
        
        # Run all strategies in parallel
        tasks = []
        for strategy in strategies:
            try:
                if hasattr(strategy, 'solve_task'):
                    task = strategy.solve_task("", prompt, url)
                    tasks.append(task)
            except Exception as e:
                logging.warning(f"Strategy failed: {e}")
                continue
        
        if not tasks:
            return []
        
        # Wait for all strategies to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and empty results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logging.warning(f"Strategy returned error: {result}")
                continue
            if result and len(result) > 0:
                valid_results.append(result)
        
        if not valid_results:
            return []
        
        # Score each result
        scored_results = []
        for actions in valid_results:
            score = self._score_actions(actions, prompt, parsed_task)
            scored_results.append((score, actions))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Return best result
        if scored_results:
            best_score, best_actions = scored_results[0]
            logging.info(f"Ensemble selected best strategy with score: {best_score:.2f}")
            return best_actions
        
        return []
    
    def _score_actions(self, actions: List[Dict[str, Any]], prompt: str, parsed_task: Optional[Dict[str, Any]] = None) -> float:
        """Score action sequence quality"""
        if not actions:
            return 0.0
        
        score = 0.0
        
        # Base score for having actions
        score += 10.0
        
        # Bonus for proper structure
        has_navigate = any(a.get("type") == "NavigateAction" for a in actions)
        has_screenshot = any(a.get("type") == "ScreenshotAction" for a in actions)
        has_wait = any(a.get("type") == "WaitAction" for a in actions)
        
        if has_navigate:
            score += 5.0
        if has_screenshot:
            score += 3.0
        if has_wait:
            score += 2.0
        
        # Bonus for action count (not too few, not too many)
        action_count = len(actions)
        if 3 <= action_count <= 15:
            score += 5.0
        elif action_count > 15:
            score += 2.0  # Too many actions
        
        # Bonus for selector quality
        for action in actions:
            if action.get("type") in ["ClickAction", "TypeAction"]:
                selector = action.get("selector")
                if selector:
                    # Multiple selector strategies
                    if selector.get("type") in ["tagContainsSelector", "attributeValueSelector"]:
                        score += 1.0
                    # Enhanced selectors
                    if selector.get("_enhanced_selectors"):
                        score += 2.0
        
        # Bonus for task-specific actions
        if parsed_task:
            if parsed_task.get("has_login"):
                has_type = any(a.get("type") == "TypeAction" for a in actions)
                has_click = any(a.get("type") == "ClickAction" for a in actions)
                if has_type and has_click:
                    score += 5.0
            
            if parsed_task.get("has_form"):
                type_count = sum(1 for a in actions if a.get("type") == "TypeAction")
                if type_count >= 2:
                    score += 3.0
        
        # Penalty for redundant actions
        action_types = [a.get("type") for a in actions]
        if action_types.count("ScreenshotAction") > 5:
            score -= 2.0  # Too many screenshots
        
        return score

