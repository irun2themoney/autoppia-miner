"""
Dynamic Zero Anti-Overfitting System
Prevents pattern memorization and promotes generalization
Based on Autoppia's Dynamic Zero: The Overfitting Punisher
"""
from typing import Dict, Any, List, Optional
import random
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta


class AntiOverfittingSystem:
    """
    Prevents overfitting by:
    1. Adding controlled randomness to pattern matching
    2. Detecting and penalizing exact pattern memorization
    3. Promoting task diversity and generalization
    4. Balancing pattern reuse with adaptation
    """
    
    def __init__(self):
        self.pattern_usage_counts = defaultdict(int)  # Track how often patterns are reused
        self.task_variations = defaultdict(set)  # Track variations of similar tasks
        self.overfitting_penalty = 0.0  # Penalty score for overfitting
        self.diversity_bonus = 0.0  # Bonus for handling diverse tasks
        
        # Overfitting thresholds
        self.max_pattern_reuse = 5  # Max times to reuse exact pattern before penalty
        self.similarity_threshold = 0.85  # Above this = potential overfitting
        self.diversity_window = 100  # Last N tasks to check for diversity
        
        # Recent task history for diversity tracking
        self.recent_tasks = []
    
    def should_use_pattern(
        self, 
        pattern_similarity: float, 
        pattern_key: str,
        current_task: str,
        url: str
    ) -> tuple[bool, float]:
        """
        Determine if a pattern should be used, with overfitting protection
        
        Returns:
            (should_use: bool, confidence_adjustment: float)
        """
        # Track pattern usage
        self.pattern_usage_counts[pattern_key] += 1
        usage_count = self.pattern_usage_counts[pattern_key]
        
        # Track task diversity
        task_hash = self._hash_task(current_task, url)
        self.recent_tasks.append({
            "hash": task_hash,
            "pattern_key": pattern_key,
            "similarity": pattern_similarity,
            "timestamp": datetime.now()
        })
        
        # Keep only recent tasks
        if len(self.recent_tasks) > self.diversity_window:
            self.recent_tasks.pop(0)
        
        # Calculate diversity score
        diversity_score = self._calculate_diversity_score()
        
        # Overfitting detection
        is_overfitting = False
        confidence_penalty = 0.0
        
        # Penalty 1: Too high similarity (memorization)
        if pattern_similarity > self.similarity_threshold:
            confidence_penalty += (pattern_similarity - self.similarity_threshold) * 0.3
            is_overfitting = True
        
        # Penalty 2: Pattern used too many times (rigid memorization)
        if usage_count > self.max_pattern_reuse:
            excess_uses = usage_count - self.max_pattern_reuse
            confidence_penalty += excess_uses * 0.1
            is_overfitting = True
        
        # Penalty 3: Low task diversity (same tasks repeatedly)
        if diversity_score < 0.3:  # Less than 30% unique tasks
            confidence_penalty += (0.3 - diversity_score) * 0.2
            is_overfitting = True
        
        # Apply penalties
        adjusted_confidence = max(0.0, pattern_similarity - confidence_penalty)
        
        # Decision: Use pattern if confidence is still high enough after penalties
        should_use = adjusted_confidence >= 0.5  # Minimum 50% confidence after penalties
        
        # Add controlled randomness to prevent rigid matching
        if should_use and pattern_similarity > 0.9:
            # For very high similarity, add small randomness to force adaptation
            random_factor = random.uniform(0.95, 1.0)  # 5% randomness
            adjusted_confidence *= random_factor
            
            # Occasionally force new generation even for high similarity
            if random.random() < 0.1:  # 10% chance
                should_use = False
        
        return should_use, adjusted_confidence
    
    def _hash_task(self, task: str, url: str) -> str:
        """Create a hash for task diversity tracking"""
        # Normalize task (remove specific values)
        normalized = task.lower()
        # Remove credentials
        import re
        normalized = re.sub(r'username[:\s]+[^\s]+', 'username:XXX', normalized)
        normalized = re.sub(r'password[:\s]+[^\s]+', 'password:XXX', normalized)
        normalized = re.sub(r'email[:\s]+[^\s@]+@[^\s@]+\.[^\s@]+', 'email:XXX@XXX.XXX', normalized)
        
        # Hash
        combined = f"{normalized}|{url}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _calculate_diversity_score(self) -> float:
        """Calculate task diversity score (0.0 = no diversity, 1.0 = high diversity)"""
        if len(self.recent_tasks) < 5:
            return 1.0  # Not enough data, assume diverse
        
        # Count unique task hashes
        unique_tasks = len(set(t["hash"] for t in self.recent_tasks))
        total_tasks = len(self.recent_tasks)
        
        # Diversity = unique tasks / total tasks
        diversity = unique_tasks / total_tasks if total_tasks > 0 else 0.0
        
        return diversity
    
    def add_variation(self, task: str, url: str, actions: List[Dict[str, Any]]):
        """Record a task variation to promote generalization"""
        task_hash = self._hash_task(task, url)
        pattern_key = f"{task_hash}|{url}"
        
        # Track variations
        self.task_variations[pattern_key].add(task_hash)
    
    def get_adaptation_factor(self, pattern_similarity: float) -> float:
        """
        Get adaptation factor to modify actions
        Higher factor = more adaptation needed
        """
        if pattern_similarity < 0.7:
            return 1.0  # Low similarity, full adaptation
        elif pattern_similarity < 0.85:
            return 0.7  # Medium similarity, moderate adaptation
        else:
            return 0.5  # High similarity, but still adapt
    
    def should_force_new_generation(
        self,
        pattern_key: str,
        recent_success_rate: float
    ) -> bool:
        """
        Force new generation if pattern is failing
        (prevents overfitting to failing patterns)
        """
        usage_count = self.pattern_usage_counts.get(pattern_key, 0)
        
        # If pattern used many times but success rate is low, force new generation
        if usage_count > 3 and recent_success_rate < 0.5:
            return True
        
        return False
    
    def get_overfitting_metrics(self) -> Dict[str, Any]:
        """Get metrics about overfitting status"""
        diversity_score = self._calculate_diversity_score()
        
        # Count overused patterns
        overused_patterns = sum(
            1 for count in self.pattern_usage_counts.values() 
            if count > self.max_pattern_reuse
        )
        
        return {
            "diversity_score": round(diversity_score, 3),
            "overused_patterns": overused_patterns,
            "total_patterns": len(self.pattern_usage_counts),
            "recent_tasks_count": len(self.recent_tasks),
            "is_overfitting": diversity_score < 0.3 or overused_patterns > 5
        }


# Global instance
anti_overfitting = AntiOverfittingSystem()

