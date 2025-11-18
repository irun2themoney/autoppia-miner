"""Enhanced template agent with pattern learning and vector memory"""
from typing import Dict, Any, List
from .base import BaseAgent
from .template import TemplateAgent
from ..utils.task_complexity import TaskComplexityAnalyzer
from ..utils.pattern_learner import PatternLearner
from ..utils.vector_memory import VectorMemory


class HybridAgent(BaseAgent):
    """Enhanced template agent with learning capabilities"""
    
    def __init__(self):
        self.template_agent = TemplateAgent()
        self.complexity_analyzer = TaskComplexityAnalyzer()
        self.pattern_learner = PatternLearner()
        self.vector_memory = VectorMemory(max_memories=1000)  # Top tier: vector store memory
    
    async def solve_task(
        self,
        task_id: str,
        prompt: str,
        url: str
    ) -> List[Dict[str, Any]]:
        """Solve task using hybrid strategy"""
        import logging
        
        # Check vector memory first (top tier optimization)
        memory_actions = self.vector_memory.get_best_actions(prompt, url)
        if memory_actions:
            logging.info(f"Using vector memory recall for task: {prompt[:50]}...")
            return memory_actions
        
        # Check for learned patterns
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
        
        # All tasks use enhanced template agent
        logging.info(f"Using enhanced template agent for task: {prompt[:50]}...")
        try:
            actions = await self.template_agent.solve_task(task_id, prompt, url)
            
            # Record successful pattern (if we got valid actions)
            if actions and len(actions) > 0:
                # Store in vector memory (top tier optimization)
                parsed_task = self.complexity_analyzer.analyze(prompt, url)
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

