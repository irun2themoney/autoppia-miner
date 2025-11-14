"""Base agent interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """Base interface for web agents"""
    
    @abstractmethod
    async def solve_task(
        self, 
        task_id: str, 
        prompt: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Solve a task and return IWA BaseAction format actions
        
        Args:
            task_id: Unique task identifier
            prompt: Task description
            url: Target URL
            
        Returns:
            List of IWA BaseAction objects
        """
        pass

