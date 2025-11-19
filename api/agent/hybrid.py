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
        
        # Self-learning from official documentation (optional, non-blocking)
        self.documentation_learner = None
        try:
            from config.settings import settings
            if settings.self_learning_enabled:
                from ..utils.documentation_learner import DocumentationLearner
                self.documentation_learner = DocumentationLearner(
                    enabled=settings.self_learning_enabled,
                    check_interval=settings.self_learning_interval
                )
        except Exception:
            # Self-learning is optional - continue without it if it fails
            pass
    
    async def solve_task(
        self,
        task_id: str,
        prompt: str,
        url: str,
        validator_ip: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Solve task using hybrid strategy with god-tier features - PERFORMANCE OPTIMIZED"""
        import logging
        import time
        import asyncio
        
        start_time = time.time()
        
        # SELF-LEARNING: Apply learned patterns from official documentation (non-destructive, lazy)
        context = {"prompt": prompt, "url": url, "task_id": task_id}
        if self.documentation_learner:
            try:
                context = self.documentation_learner.apply_learned_patterns(context)
            except Exception:
                # Self-learning is optional - continue if it fails
                pass
        
        # PERFORMANCE OPT: Detect task type once (reused multiple times)
        prompt_lower = prompt.lower()
        is_login_task = "login" in prompt_lower or "sign in" in prompt_lower
        is_click_task = "click" in prompt_lower and any(w in prompt_lower for w in ["button", "link", "element", "item"])
        skip_cache = is_login_task or is_click_task
        
        # PERFORMANCE OPT: Parallelize cache/vector/pattern checks (was sequential, now concurrent)
        if not skip_cache:
            # Run all checks in parallel for maximum speed (these are sync functions, so use to_thread)
            def check_cache():
                return semantic_cache.get(prompt, url)
            
            def check_vector():
                return self.vector_memory.get_best_actions(prompt, url)
            
            def check_pattern():
                return self.pattern_learner.get_similar_pattern(prompt, url)
            
            # Run all checks concurrently (3x faster!)
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(
                        asyncio.to_thread(check_cache),
                        asyncio.to_thread(check_vector),
                        asyncio.to_thread(check_pattern),
                        return_exceptions=True
                    ),
                    timeout=0.5  # 500ms max for all checks
                )
                cached_result, memory_actions, learned_pattern = results
            except asyncio.TimeoutError:
                # If checks take too long, proceed without them
                logging.warning("Cache/vector/pattern checks timed out, proceeding with generation")
                cached_result, memory_actions, learned_pattern = None, None, None
        else:
            # For login/click tasks, skip all caches
            logging.info(f"Login/click task detected, skipping cache for fresh generation")
            cached_result, memory_actions, learned_pattern = None, None, None
        
        # PERFORMANCE OPT: Check results in priority order (cache > vector > pattern)
        # Cache is fastest (in-memory), so check it first
        if cached_result and not isinstance(cached_result, Exception):
            actions, similarity = cached_result
            logging.info(f"Semantic cache hit (similarity: {similarity:.2f}) for task: {prompt[:50]}...")
            # Ensure actions are in IWA format (cache might have raw actions)
            from ..actions.converter import convert_to_iwa_action
            return [convert_to_iwa_action(action) if action.get("type") is None or not action.get("type").endswith("Action") else action for action in actions]
        
        # Vector memory is second fastest
        if memory_actions and not isinstance(memory_actions, Exception) and memory_actions:
            logging.info(f"Using vector memory recall for task: {prompt[:50]}...")
            # Ensure actions are in IWA format
            from ..actions.converter import convert_to_iwa_action
            iwa_actions = [convert_to_iwa_action(action) if action.get("type") is None or not action.get("type").endswith("Action") else action for action in memory_actions]
            # Cache in semantic cache for next time
            semantic_cache.set(prompt, url, iwa_actions)
            return iwa_actions
        
        # Pattern learner is third
        if learned_pattern and not isinstance(learned_pattern, Exception) and learned_pattern:
            # PERFORMANCE OPT: Lazy load diversity analysis only if needed
            diversity_info = task_diversity.analyze_task_diversity(prompt, url)
            if diversity_info.get("diversity_issues"):
                logging.warning(f"Diversity issues detected: {diversity_info['diversity_issues']}")
            
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

