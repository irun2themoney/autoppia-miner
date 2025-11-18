"""Enhanced template agent with pattern learning and vector memory"""
from typing import Dict, Any, List, Optional
from .base import BaseAgent
from .template import TemplateAgent
from ..utils.task_complexity import TaskComplexityAnalyzer
from ..utils.pattern_learner import PatternLearner
from ..utils.vector_memory import VectorMemory
from ..utils.ensemble_voting import ensemble_voting
from ..utils.semantic_cache import semantic_cache
from ..utils.validator_learner import validator_learner
from ..utils.anti_overfitting import anti_overfitting
from ..utils.task_diversity import task_diversity


class HybridAgent(BaseAgent):
    """Enhanced template agent with learning capabilities and god-tier features"""
    
    def __init__(self):
        self.template_agent = TemplateAgent()
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.pattern_learner = PatternLearner()
        self.vector_memory = VectorMemory(max_memories=1000)  # Top tier: vector store memory
    
    async def solve_task(
        self,
        task_id: str,
        prompt: str,
        url: str,
        validator_ip: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Solve task using hybrid strategy with god-tier features"""
        import logging
        import time
        
        start_time = time.time()
        
        # GOD-TIER: Check semantic cache first (advanced caching)
        # For login and click tasks, be more strict - skip cache to ensure fresh generation
        prompt_lower = prompt.lower()
        is_login_task = "login" in prompt_lower or "sign in" in prompt_lower
        is_click_task = "click" in prompt_lower and any(w in prompt_lower for w in ["button", "link", "element", "item"])
        
        # For login and click tasks, skip cache to ensure fresh generation (prevents incomplete cached results)
        if not is_login_task and not is_click_task:
            cached_result = semantic_cache.get(prompt, url)
            if cached_result:
                actions, similarity = cached_result
                logging.info(f"Semantic cache hit (similarity: {similarity:.2f}) for task: {prompt[:50]}...")
                # Ensure actions are in IWA format (cache might have raw actions)
                from ..actions.converter import convert_to_iwa_action
                return [convert_to_iwa_action(action) if action.get("type") is None or not action.get("type").endswith("Action") else action for action in actions]
        else:
            # For login tasks, always generate fresh to ensure complete actions
            logging.info(f"Login task detected, skipping cache for fresh generation")
            cached_result = None
        
        # Check vector memory (top tier optimization)
        # For login and click tasks, skip vector memory to ensure fresh generation
        if not is_login_task and not is_click_task:
            memory_actions = self.vector_memory.get_best_actions(prompt, url)
            if memory_actions:
                logging.info(f"Using vector memory recall for task: {prompt[:50]}...")
                # Ensure actions are in IWA format
                from ..actions.converter import convert_to_iwa_action
                iwa_actions = [convert_to_iwa_action(action) if action.get("type") is None or not action.get("type").endswith("Action") else action for action in memory_actions]
                # Cache in semantic cache
                semantic_cache.set(prompt, url, iwa_actions)
                return iwa_actions
        
        # DYNAMIC ZERO: Analyze task diversity
        diversity_info = task_diversity.analyze_task_diversity(prompt, url)
        if diversity_info.get("diversity_issues"):
            logging.warning(f"Diversity issues detected: {diversity_info['diversity_issues']}")
        
        # Check for learned patterns (with anti-overfitting protection)
        # For login and click tasks, skip pattern learner to ensure fresh generation
        learned_pattern = None
        if not is_login_task and not is_click_task:
            learned_pattern = self.pattern_learner.get_similar_pattern(prompt, url)
        if learned_pattern:
            # DYNAMIC ZERO: Adapt pattern for variation if needed
            adaptation_factor = anti_overfitting.get_adaptation_factor(0.8)  # Assume high similarity
            if adaptation_factor < 1.0:
                logging.info(f"Adapting pattern for variation (factor: {adaptation_factor})")
                learned_pattern = task_diversity.adapt_actions_for_variation(
                    learned_pattern, diversity_info
                )
            
            logging.info(f"Using learned pattern for task: {prompt[:50]}...")
            # Ensure actions are in IWA format
            from ..actions.converter import convert_to_iwa_action
            iwa_actions = [convert_to_iwa_action(action) if action.get("type") is None or not action.get("type").endswith("Action") else action for action in learned_pattern]
            # Cache in semantic cache
            semantic_cache.set(prompt, url, iwa_actions)
            return iwa_actions
        
        # GOD-TIER: Multi-agent ensemble voting
        # Prepare multiple strategies
        strategies = [self.template_agent]
        
        # Add vector memory as a strategy (if it has similar tasks)
        # Add pattern learner as a strategy (if it has similar patterns)
        
        parsed_task = self.complexity_analyzer.analyze(prompt, url)
        
        # Run ensemble voting if we have multiple strategies
        if len(strategies) > 1:
            logging.info(f"Running ensemble voting with {len(strategies)} strategies")
            try:
                actions, voting_metadata = await ensemble_voting.vote_on_actions(
                    strategies=strategies,
                    prompt=prompt,
                    url=url,
                    task_id=task_id,
                    parsed_task=parsed_task
                )
                
                if actions and len(actions) > 0:
                    # Ensure actions are in IWA format (ensemble might return raw actions)
                    from ..actions.converter import convert_to_iwa_action
                    iwa_actions = [convert_to_iwa_action(action) if action.get("type") is None or not action.get("type").endswith("Action") else action for action in actions]
                    # Cache result
                    semantic_cache.set(prompt, url, iwa_actions)
                    
                    # Store in vector memory
                    self.vector_memory.add_memory(
                        prompt=prompt,
                        url=url,
                        actions=iwa_actions,
                        success_rate=1.0,
                        task_type=parsed_task.get("task_type", "generic")
                    )
                    
                    # Record in pattern learner
                    self.pattern_learner.record_success(prompt, url, iwa_actions)
                    
                    return iwa_actions
            except Exception as e:
                logging.warning(f"Ensemble voting failed: {e}, falling back to template agent")
        
        # Fallback: Use enhanced template agent
        logging.info(f"Using enhanced template agent for task: {prompt[:50]}...")
        try:
            actions = await self.template_agent.solve_task(task_id, prompt, url)
            
            # Record successful pattern (if we got valid actions)
            if actions and len(actions) > 0:
                # Cache in semantic cache
                semantic_cache.set(prompt, url, actions)
                
                # Store in vector memory (top tier optimization)
                self.vector_memory.add_memory(
                    prompt=prompt,
                    url=url,
                    actions=actions,
                    success_rate=1.0,
                    task_type=parsed_task.get("task_type", "generic")
                )
                # Also record in pattern learner
                self.pattern_learner.record_success(prompt, url, actions)
            
            return actions
        except Exception as e:
            logging.error(f"Template agent failed: {e}")
            # Return minimal action to avoid empty response
            return [{"type": "ScreenshotAction"}]
    
    def record_validator_result(
        self,
        validator_ip: str,
        task_prompt: str,
        task_url: str,
        actions: List[Dict[str, Any]],
        success: bool,
        response_time: float,
        task_type: Optional[str] = None,
        score: Optional[float] = None
    ):
        """Record validator result for learning (GOD-TIER feature)"""
        validator_learner.record_result(
            validator_ip=validator_ip,
            task_prompt=task_prompt,
            task_url=task_url,
            actions=actions,
            success=success,
            response_time=response_time,
            task_type=task_type,
            score=score
        )

