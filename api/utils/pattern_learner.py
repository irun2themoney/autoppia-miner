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
            except:
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
        """Get similar successful pattern"""
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
                return patterns[0].get("actions")
        
        # Check for similar patterns (simple keyword matching)
        prompt_lower = prompt.lower()
        for key, patterns_list in self.patterns.items():
            if key == pattern_key:
                continue
            
            # Simple similarity check (shared keywords)
            key_prompt = key.split("|")[0]
            shared_words = set(prompt_lower.split()) & set(key_prompt.split())
            if len(shared_words) >= 2:  # At least 2 shared words
                # Check if this pattern has been successful
                best_pattern = max(patterns_list, key=lambda x: x.get("success_count", 0))
                if best_pattern.get("success_count", 0) >= 3:
                    return best_pattern.get("actions")
        
        return None

