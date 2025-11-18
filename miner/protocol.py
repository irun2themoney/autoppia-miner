"""
Synapse protocol definitions for Autoppia Subnet 36
Based on official Autoppia patterns
"""
import bittensor as bt
from typing import List, Dict, Any, Optional


class StartRoundSynapse(bt.Synapse):
    """
    Synapse for starting a new round
    Used by validators to initiate task rounds
    
    Note: Bittensor may deserialize this as a generic Synapse.
    The miner handles this by checking for round_id and task_type attributes.
    """
    # Round information
    round_id: Optional[str] = None
    task_type: Optional[str] = None
    
    # Response fields
    success: bool = False
    message: Optional[str] = None
    
    def deserialize(self) -> "StartRoundSynapse":
        """Deserialize synapse data"""
        return self


class TaskSynapse(bt.Synapse):
    """
    Main task synapse for processing IWA tasks
    Matches ApifiedWebAgent pattern
    """
    # Task input (from task.clean_task())
    id: str = ""
    prompt: str = ""
    url: str = ""
    
    # Task response
    actions: List[Dict[str, Any]] = []
    web_agent_id: str = ""
    recording: str = ""
    task_id: str = ""
    success: bool = False
    task_type: str = "generic"
    
    def deserialize(self) -> "TaskSynapse":
        """Deserialize synapse data"""
        return self

