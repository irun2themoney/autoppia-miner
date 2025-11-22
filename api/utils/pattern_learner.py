"""Learn from successful task patterns"""
from typing import Dict, Any, List, Optional
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta


class PatternLearner:
    """Learn and reuse successful patterns"""
    
    def __init__(self, cache_file: str = "/tmp/autoppia_patterns.json"):
        self.cache_file = cache_file
        self.patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.load_patterns()
    
    def load_patterns(self):
        """Load learned patterns from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.patterns = defaultdict(list, data.get("patterns", {}))
                    self.success_counts = defaultdict(int, data.get("success_counts", {}))
            except Exception:
                pass  # Start fresh if file is corrupted
    
    def save_patterns(self):
        """Save learned patterns to disk"""
        try:
            data = {
                "patterns": dict(self.patterns),
                "success_counts": dict(self.success_counts),
                "last_updated": datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Non-critical, continue without saving
    
    def get_pattern_key(self, prompt: str, url: str) -> str:
        """Generate pattern key from prompt and URL"""
        # Normalize prompt (lowercase, remove specific values)
        normalized = prompt.lower()
        # Remove specific values like usernames, passwords
        normalized = re.sub(r'username[:\s]+[^\s]+', 'username:XXX', normalized)
        normalized = re.sub(r'password[:\s]+[^\s]+', 'password:XXX', normalized)
        normalized = re.sub(r'email[:\s]+[^\s@]+@[^\s@]+\.[^\s@]+', 'email:XXX@XXX.XXX', normalized)
        
        # Use domain from URL
        domain = ""
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
            except Exception:
                pass
        
        return f"{normalized}|{domain}"
    
    def record_success(self, prompt: str, url: str, actions: List[Dict[str, Any]]):
        """Record successful pattern"""
        pattern_key = self.get_pattern_key(prompt, url)
        self.success_counts[pattern_key] += 1
        
        # Store pattern (keep last 5 successful patterns per key)
        if pattern_key not in self.patterns or len(self.patterns[pattern_key]) < 5:
            self.patterns[pattern_key].append({
                "actions": actions,
                "timestamp": datetime.now().isoformat(),
                "success_count": self.success_counts[pattern_key]
            })
        else:
            # Replace oldest pattern
            self.patterns[pattern_key].sort(key=lambda x: x.get("timestamp", ""))
            self.patterns[pattern_key][0] = {
                "actions": actions,
                "timestamp": datetime.now().isoformat(),
                "success_count": self.success_counts[pattern_key]
            }
        
        # Save periodically (every 10 successes)
        if self.success_counts[pattern_key] % 10 == 0:
            self.save_patterns()
    
    def get_similar_pattern(self, prompt: str, url: str) -> Optional[List[Dict[str, Any]]]:
        """Get similar successful pattern - Enhanced similarity matching with anti-overfitting"""
        from .anti_overfitting import anti_overfitting
        
        pattern_key = self.get_pattern_key(prompt, url)
        
        # Check exact match first
        if pattern_key in self.patterns and self.patterns[pattern_key]:
            # Return most successful pattern
            patterns = sorted(
                self.patterns[pattern_key],
                key=lambda x: x.get("success_count", 0),
                reverse=True
            )
            if patterns and patterns[0].get("success_count", 0) >= 2:
                # DYNAMIC ZERO: Check for overfitting before using pattern
                similarity = 1.0  # Exact match
                should_use, adjusted_confidence = anti_overfitting.should_use_pattern(
                    similarity, pattern_key, prompt, url
                )
                
                if should_use and adjusted_confidence >= 0.6:
                    return patterns[0].get("actions")
                # If overfitting detected, continue to similarity search for variation
        
        # Enhanced similarity check with better matching
        prompt_lower = prompt.lower()
        prompt_words = set(prompt_lower.split())
        
        best_match = None
        best_score = 0.0
        
        for key, patterns_list in self.patterns.items():
            if key == pattern_key:
                continue
            
            key_prompt = key.split("|")[0]
            key_words = set(key_prompt.split())
            
            # Calculate similarity score
            if not prompt_words or not key_words:
                continue
            
            # Jaccard similarity (intersection over union)
            intersection = len(prompt_words & key_words)
            union = len(prompt_words | key_words)
            similarity = intersection / union if union > 0 else 0.0
            
            # Bonus for task type keywords
            task_keywords = {
                "login": ["login", "sign", "authenticate"],
                "form": ["form", "fill", "submit"],
                "click": ["click", "select", "choose"],
                "search": ["search", "find", "look"],
            }
            
            for task_type, keywords in task_keywords.items():
                if any(kw in prompt_lower for kw in keywords) and any(kw in key_prompt for kw in keywords):
                    similarity += 0.2  # Bonus for same task type
                    break
            
            # URL similarity bonus
            key_url = key.split("|")[1] if "|" in key else ""
            if url and key_url:
                if url in key_url or key_url in url:
                    similarity += 0.1
            
            # Check if this pattern has been successful
            best_pattern = max(patterns_list, key=lambda x: x.get("success_count", 0))
            success_count = best_pattern.get("success_count", 0)
            
            # Weighted score (similarity * success_count)
            weighted_score = similarity * (1 + success_count * 0.1)
            
            if weighted_score > best_score and similarity >= 0.3:  # Minimum 30% similarity
                # DYNAMIC ZERO: Check for overfitting
                from .anti_overfitting import anti_overfitting
                should_use, adjusted_confidence = anti_overfitting.should_use_pattern(
                    similarity, key, prompt, url
                )
                
                if should_use and adjusted_confidence >= 0.5:
                    best_score = weighted_score
                    best_match = best_pattern.get("actions")
        
        # DYNAMIC ZERO: If best match found, add variation tracking
        if best_match:
            from .anti_overfitting import anti_overfitting
            anti_overfitting.add_variation(prompt, url, best_match)
        
        return best_match

