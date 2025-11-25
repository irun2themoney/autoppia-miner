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
        """
        Solve task using template-based action generation
        GUARANTEED to return at least one action (never empty list)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Generate actions using templates (pass task_id to skip browser automation for tests)
            raw_actions = await self.action_generator.generate(prompt, url, task_id=task_id)
            
            # CRITICAL: Ensure raw_actions is not None or empty
            if not raw_actions:
                logger.error(f"🚨 CRITICAL: action_generator.generate returned empty/None for task {task_id}")
                raw_actions = []
            
            logger.info(f"🔍 Generated {len(raw_actions)} raw actions for task {task_id}")
            
            # Convert to IWA format with error handling
            iwa_actions = []
            for i, action in enumerate(raw_actions):
                try:
                    converted = convert_to_iwa_action(action)
                    if converted:  # Only add if conversion succeeded
                        iwa_actions.append(converted)
                    else:
                        logger.warning(f"⚠️ Action {i} conversion returned None/empty, skipping")
                except Exception as e:
                    logger.error(f"❌ Error converting action {i}: {e}")
                    import traceback
                    logger.debug(f"Conversion error traceback: {traceback.format_exc()}")
                    # Skip this action, continue with others
            
            # CRITICAL: Ensure non-empty (critical for playground)
            if not iwa_actions or len(iwa_actions) == 0:
                logger.error(f"🚨 CRITICAL: All actions failed conversion or were empty for task {task_id}")
                # GUARANTEED MINIMAL ACTIONS
                fallback_url = url if url else "https://example.com"
                iwa_actions = [
                    {"type": "NavigateAction", "url": fallback_url},
                    {"type": "WaitAction", "timeSeconds": 1.0},
                    {"type": "ScreenshotAction"}
                ]
                logger.error(f"🚨 Returning GUARANTEED minimal actions: {len(iwa_actions)} actions")
            
            logger.info(f"✅ Returning {len(iwa_actions)} IWA actions for task {task_id}")
            return iwa_actions
            
        except Exception as e:
            # CRITICAL: Even if everything fails, return guaranteed minimal actions
            import traceback
            logger.error(f"🚨 FATAL ERROR in solve_task for task {task_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # GUARANTEED MINIMAL FALLBACK
            fallback_url = url if url else "https://example.com"
            guaranteed_actions = [
                {"type": "NavigateAction", "url": fallback_url},
                {"type": "WaitAction", "timeSeconds": 1.0},
                {"type": "ScreenshotAction"}
            ]
            
            logger.error(f"🚨 Returning GUARANTEED minimal actions after fatal error: {len(guaranteed_actions)} actions")
            return guaranteed_actions

