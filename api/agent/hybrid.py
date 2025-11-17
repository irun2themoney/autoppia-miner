"""Hybrid agent that routes tasks to best agent based on complexity"""
from typing import Dict, Any, List
from .base import BaseAgent
from .template import TemplateAgent
from .chutes import ChutesAgent
from ..utils.task_complexity import TaskComplexityAnalyzer
from ..utils.pattern_learner import PatternLearner


class HybridAgent(BaseAgent):
    """Hybrid agent that intelligently routes tasks"""
    
    def __init__(self):
        self.template_agent = TemplateAgent()
        self.chutes_agent = ChutesAgent()
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.pattern_learner = PatternLearner()
    
    async def solve_task(
        self,
        task_id: str,
        prompt: str,
        url: str
    ) -> List[Dict[str, Any]]:
        """Solve task using hybrid strategy"""
        import logging
        
        # Check for learned patterns first
        learned_pattern = self.pattern_learner.get_similar_pattern(prompt, url)
        if learned_pattern:
            logging.info(f"Using learned pattern for task: {prompt[:50]}...")
            return learned_pattern
        
        # Analyze complexity
        complexity = self.complexity_analyzer.analyze(prompt, url)
        
        # Route based on complexity
        if complexity["complexity"] == "low" and not complexity["requires_llm"]:
            # Simple tasks: use template (faster, cheaper)
            logging.info(f"Using template agent for simple task: {prompt[:50]}...")
            try:
                actions = await self.template_agent.solve_task(task_id, prompt, url)
                return actions
            except Exception as e:
                logging.warning(f"Template agent failed, falling back to LLM: {e}")
                # Fall through to LLM
        
        # Complex tasks: use LLM
        logging.info(f"Using LLM agent for {'complex' if complexity['complexity'] == 'high' else 'medium'} task: {prompt[:50]}...")
        try:
            actions = await self.chutes_agent.solve_task(task_id, prompt, url)
            
            # Record successful pattern (if we got valid actions)
            if actions and len(actions) > 0:
                # Note: In production, we'd need feedback on success
                # For now, we record patterns that generate actions
                # self.pattern_learner.record_success(prompt, url, actions)
                pass
            
            return actions
        except Exception as e:
            logging.warning(f"LLM agent failed, falling back to template: {e}")
            # Final fallback to template
            return await self.template_agent.solve_task(task_id, prompt, url)

