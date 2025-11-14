"""Template-based agent implementation"""
from typing import Dict, Any, List
from .base import BaseAgent
from ..actions.generator import ActionGenerator
from ..actions.converter import convert_to_iwa_action


class TemplateAgent(BaseAgent):
    """Template-based agent (current implementation)"""
    
    def __init__(self):
        self.action_generator = ActionGenerator()
    
    async def solve_task(
        self, 
        task_id: str, 
        prompt: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """Solve task using template-based action generation"""
        # Generate actions using templates
        raw_actions = self.action_generator.generate(prompt, url)
        
        # Convert to IWA format
        iwa_actions = [
            convert_to_iwa_action(action) 
            for action in raw_actions
        ]
        
        # Ensure non-empty (critical for playground)
        if not iwa_actions:
            iwa_actions = [{"type": "ScreenshotAction"}]
        
        return iwa_actions

