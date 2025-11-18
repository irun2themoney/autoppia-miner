"""Multi-Agent Ensemble Voting - Run multiple strategies in parallel and vote on best actions"""
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class EnsembleVoting:
    """
    Multi-agent ensemble voting system
    Runs 3-5 different agent strategies in parallel and votes on best action sequence
    """
    
    def __init__(self):
        self.voting_history = []  # Track voting decisions for learning
    
    async def vote_on_actions(
        self,
        strategies: List[Any],
        prompt: str,
        url: str,
        task_id: str = "",
        parsed_task: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Run multiple strategies in parallel and vote on best action sequence
        
        Args:
            strategies: List of agent strategies to run
            prompt: Task prompt
            url: Task URL
            task_id: Task ID
            parsed_task: Parsed task information
            
        Returns:
            (best_actions, voting_metadata)
        """
        if not strategies:
            logger.warning("No strategies provided for ensemble voting")
            return [], {}
        
        logger.info(f"Running ensemble voting with {len(strategies)} strategies")
        
        # Run all strategies in parallel
        tasks = []
        strategy_names = []
        
        for i, strategy in enumerate(strategies):
            strategy_name = self._get_strategy_name(strategy, i)
            strategy_names.append(strategy_name)
            
            try:
                if hasattr(strategy, 'solve_task'):
                    task = strategy.solve_task(task_id, prompt, url)
                    tasks.append((strategy_name, task))
                elif callable(strategy):
                    # Strategy is a function
                    task = strategy(prompt, url)
                    tasks.append((strategy_name, task))
                else:
                    logger.warning(f"Strategy {strategy_name} is not callable")
            except Exception as e:
                logger.warning(f"Strategy {strategy_name} failed to initialize: {e}")
                continue
        
        if not tasks:
            logger.warning("No valid strategies to run")
            return [], {}
        
        # Wait for all strategies to complete
        results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        # Collect valid results with strategy names
        valid_results = []
        for (strategy_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.warning(f"Strategy {strategy_name} returned error: {result}")
                continue
            if result and isinstance(result, list) and len(result) > 0:
                valid_results.append((strategy_name, result))
        
        if not valid_results:
            logger.warning("No valid results from any strategy")
            return [], {}
        
        logger.info(f"Got {len(valid_results)} valid results from {len(strategies)} strategies")
        
        # Score each result
        scored_results = []
        for strategy_name, actions in valid_results:
            score = self._score_actions(actions, prompt, parsed_task, strategy_name)
            scored_results.append((score, strategy_name, actions))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # Voting: Use consensus if multiple strategies agree
        consensus_actions = self._find_consensus(valid_results)
        
        # Choose best: consensus if available, otherwise highest score
        if consensus_actions:
            best_actions = consensus_actions
            best_strategy = "consensus"
            best_score = scored_results[0][0] if scored_results else 0.0
            logger.info(f"Ensemble voting: Using consensus from {len(valid_results)} strategies")
        else:
            best_score, best_strategy, best_actions = scored_results[0]
            logger.info(f"Ensemble voting: Selected {best_strategy} with score {best_score:.2f}")
        
        # Record voting decision
        voting_metadata = {
            "strategies_run": len(strategies),
            "valid_results": len(valid_results),
            "best_strategy": best_strategy,
            "best_score": best_score,
            "all_scores": {name: score for score, name, _ in scored_results},
            "used_consensus": consensus_actions is not None
        }
        
        self.voting_history.append({
            "prompt": prompt[:100],  # Store first 100 chars
            "url": url,
            "voting_metadata": voting_metadata,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Keep only last 100 voting decisions
        if len(self.voting_history) > 100:
            self.voting_history.pop(0)
        
        return best_actions, voting_metadata
    
    def _get_strategy_name(self, strategy: Any, index: int) -> str:
        """Get name for strategy"""
        if hasattr(strategy, '__class__'):
            return strategy.__class__.__name__
        elif hasattr(strategy, '__name__'):
            return strategy.__name__
        else:
            return f"Strategy_{index}"
    
    def _score_actions(
        self,
        actions: List[Dict[str, Any]],
        prompt: str,
        parsed_task: Optional[Dict[str, Any]],
        strategy_name: str
    ) -> float:
        """Score action sequence quality"""
        if not actions:
            return 0.0
        
        score = 0.0
        
        # Base score for having actions
        score += 10.0
        
        # Bonus for proper structure
        action_types = [a.get("action_type") or a.get("type", "") for a in actions]
        has_navigate = any("navigate" in str(t).lower() for t in action_types)
        has_screenshot = any("screenshot" in str(t).lower() for t in action_types)
        has_wait = any("wait" in str(t).lower() for t in action_types)
        
        if has_navigate:
            score += 5.0
        if has_screenshot:
            score += 3.0
        if has_wait:
            score += 2.0
        
        # Bonus for action count (optimal range: 3-15)
        action_count = len(actions)
        if 3 <= action_count <= 15:
            score += 5.0
        elif 5 <= action_count <= 20:
            score += 3.0
        elif action_count > 20:
            score += 1.0  # Too many actions
        
        # Bonus for selector quality
        for action in actions:
            action_type = action.get("action_type") or action.get("type", "")
            if "click" in str(action_type).lower() or "type" in str(action_type).lower():
                selector = action.get("selector")
                if selector:
                    # Multiple selector strategies
                    if isinstance(selector, list) and len(selector) > 1:
                        score += 2.0  # Multiple fallback selectors
                    elif isinstance(selector, dict):
                        selector_type = selector.get("type", "")
                        if selector_type in ["tagContainsSelector", "attributeValueSelector"]:
                            score += 1.0
        
        # Bonus for task-specific actions
        if parsed_task:
            task_type = parsed_task.get("task_type", "")
            if "login" in task_type.lower():
                has_type = any("type" in str(t).lower() for t in action_types)
                has_click = any("click" in str(t).lower() for t in action_types)
                if has_type and has_click:
                    score += 5.0
            
            if "form" in task_type.lower():
                type_count = sum(1 for t in action_types if "type" in str(t).lower())
                if type_count >= 2:
                    score += 3.0
        
        # Penalty for redundant actions
        screenshot_count = sum(1 for t in action_types if "screenshot" in str(t).lower())
        if screenshot_count > 5:
            score -= 2.0  # Too many screenshots
        
        # Strategy-specific bonuses
        if "template" in strategy_name.lower():
            score += 1.0  # Template is reliable
        elif "vector" in strategy_name.lower() or "memory" in strategy_name.lower():
            score += 2.0  # Memory-based is often better
        
        return score
    
    def _find_consensus(
        self,
        results: List[Tuple[str, List[Dict[str, Any]]]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Find consensus among multiple strategies
        If 2+ strategies produce similar actions, use consensus
        """
        if len(results) < 2:
            return None
        
        # Compare action sequences
        # Simple consensus: if 2+ strategies have similar action counts and types
        action_signatures = []
        for strategy_name, actions in results:
            signature = self._get_action_signature(actions)
            action_signatures.append((strategy_name, signature, actions))
        
        # Find similar signatures (consensus)
        signature_groups = {}
        for strategy_name, signature, actions in action_signatures:
            if signature not in signature_groups:
                signature_groups[signature] = []
            signature_groups[signature].append((strategy_name, actions))
        
        # Find largest consensus group
        largest_group = max(signature_groups.values(), key=len)
        
        if len(largest_group) >= 2:
            # Use consensus: take actions from highest-scoring strategy in group
            # For now, just return first one (they're similar anyway)
            _, consensus_actions = largest_group[0]
            logger.info(f"Found consensus among {len(largest_group)} strategies")
            return consensus_actions
        
        return None
    
    def _get_action_signature(self, actions: List[Dict[str, Any]]) -> str:
        """Get signature for action sequence (for consensus detection)"""
        if not actions:
            return "empty"
        
        # Create signature from action types and counts
        action_types = []
        for action in actions:
            action_type = action.get("action_type") or action.get("type", "")
            action_types.append(str(action_type).lower())
        
        # Create signature: "navigate-wait-screenshot-click-wait-screenshot"
        signature = "-".join(action_types[:10])  # First 10 actions
        return signature
    
    def get_voting_stats(self) -> Dict[str, Any]:
        """Get statistics about voting decisions"""
        if not self.voting_history:
            return {"total_votes": 0}
        
        consensus_count = sum(1 for v in self.voting_history if v["voting_metadata"].get("used_consensus"))
        
        strategy_wins = Counter()
        for vote in self.voting_history:
            best_strategy = vote["voting_metadata"].get("best_strategy", "unknown")
            strategy_wins[best_strategy] += 1
        
        return {
            "total_votes": len(self.voting_history),
            "consensus_count": consensus_count,
            "consensus_rate": consensus_count / len(self.voting_history) if self.voting_history else 0,
            "strategy_wins": dict(strategy_wins)
        }


# Global instance
ensemble_voting = EnsembleVoting()

