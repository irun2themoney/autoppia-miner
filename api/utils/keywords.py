"""Keyword extraction utilities"""
from typing import Dict, List


def extract_keywords(prompt: str) -> Dict[str, List[str]]:
    """Extract keywords from prompt for smart action generation"""
    prompt_lower = prompt.lower()
    
    # Action keywords
    action_keywords = []
    if any(w in prompt_lower for w in ["click", "select", "choose", "pick"]):
        action_keywords.append("click")
    if any(w in prompt_lower for w in ["type", "enter", "fill", "input"]):
        action_keywords.append("type")
    if any(w in prompt_lower for w in ["search", "find", "look"]):
        action_keywords.append("search")
    if any(w in prompt_lower for w in ["switch", "toggle", "change", "view"]):
        action_keywords.append("switch")
    
    # Target keywords (what to interact with)
    target_keywords = []
    for word in ["month", "week", "day", "year", "button", "link", "submit", "login"]:
        if word in prompt_lower:
            target_keywords.append(word)
    
    return {"actions": action_keywords, "targets": target_keywords}

